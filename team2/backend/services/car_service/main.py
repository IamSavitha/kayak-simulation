"""
Car Service - Port 8004
"""
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import uvicorn

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.schemas.car_schemas import (
    CarCreate, CarUpdate, CarResponse, CarSearchResponse
)
from backend.repositories.car_repository import CarRepository
from backend.kafka.producer import KafkaProducerService
from backend.kafka.topics import EVENT_LISTING_CREATED, EVENT_LISTING_UPDATED, EVENT_LISTING_DELETED, LISTING_TYPE_CAR

app = FastAPI(
    title="Car Service",
    description="Team 2 - Car Listing Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "Car Service", "port": 8004, "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "car-service"}

@app.post("/cars", response_model=CarResponse, status_code=201)
async def create_car(car: CarCreate):
    """Create a new car listing"""
    try:
        car_data = car.model_dump()
        created_car = CarRepository.create(car_data)
        
        if not created_car:
            raise HTTPException(status_code=500, detail="Failed to create car")
        
        await KafkaProducerService.send_listing_event(
            event_type=EVENT_LISTING_CREATED,
            listing_type=LISTING_TYPE_CAR,
            listing_id=created_car['car_id'],
            data={
                'car_type': created_car['car_type'],
                'company_provider_name': created_car['company_provider_name'],
                'daily_rental_price': float(created_car['daily_rental_price']),
                'location_city': created_car.get('location_city'),
                'location_state': created_car.get('location_state'),
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return created_car
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/cars/{car_id}", response_model=CarResponse)
async def get_car(car_id: str):
    """Get car by ID"""
    car = CarRepository.get_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@app.put("/cars/{car_id}", response_model=CarResponse)
async def update_car(car_id: str, car_update: CarUpdate):
    """Update car"""
    existing = CarRepository.get_by_id(car_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Car not found")
    
    update_data = car_update.model_dump(exclude_unset=True)
    if not update_data:
        return existing
    
    updated_car = CarRepository.update(car_id, update_data)
    
    if not updated_car:
        raise HTTPException(status_code=500, detail="Failed to update car")
    
    await KafkaProducerService.send_listing_event(
        event_type=EVENT_LISTING_UPDATED,
        listing_type=LISTING_TYPE_CAR,
        listing_id=car_id,
        data={
            'updated_fields': list(update_data.keys()),
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    return updated_car

@app.delete("/cars/{car_id}", status_code=204)
async def delete_car(car_id: str):
    """Delete car"""
    existing = CarRepository.get_by_id(car_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Car not found")
    
    success = CarRepository.delete(car_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete car")
    
    await KafkaProducerService.send_listing_event(
        event_type=EVENT_LISTING_DELETED,
        listing_type=LISTING_TYPE_CAR,
        listing_id=car_id,
        data={'timestamp': datetime.utcnow().isoformat()}
    )
    
    return None

@app.get("/cars/search", response_model=CarSearchResponse)
async def search_cars(
    location: Optional[str] = Query(None, description="City or state"),
    city: Optional[str] = Query(None, description="City name"),
    state: Optional[str] = Query(None, description="State abbreviation"),
    car_type: Optional[str] = Query(None, description="Car type (SUV, Sedan, etc.)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum daily rental price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum daily rental price"),
    transmission_type: Optional[str] = Query(None, description="Automatic or Manual"),
    min_seats: Optional[int] = Query(None, ge=2, description="Minimum number of seats"),
    max_seats: Optional[int] = Query(None, le=8, description="Maximum number of seats"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """Search cars with filters"""
    search_params = {
        'location': location,
        'city': city,
        'state': state,
        'car_type': car_type,
        'min_price': min_price,
        'max_price': max_price,
        'transmission_type': transmission_type,
        'min_seats': min_seats,
        'max_seats': max_seats,
        'page': page,
        'page_size': page_size
    }
    
    search_params = {k: v for k, v in search_params.items() if v is not None}
    result = CarRepository.search(search_params)
    
    return CarSearchResponse(
        cars=[CarResponse(**c) for c in result['cars']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )

@app.post("/cars/{car_id}/images", status_code=201)
async def upload_car_image(car_id: str, image: UploadFile = File(...)):
    """Upload car image"""
    car = CarRepository.get_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    image_data = await image.read()
    metadata = {
        'filename': image.filename,
        'content_type': image.content_type,
        'size': len(image_data)
    }
    
    image_id = CarRepository.save_image(car_id, image_data, metadata)
    return {"image_id": image_id, "message": "Image uploaded successfully"}

@app.get("/cars/{car_id}/images", status_code=200)
async def get_car_images(car_id: str):
    """Get car images"""
    images = CarRepository.get_images(car_id)
    return {"images": images}

@app.put("/cars/{car_id}/availability", status_code=200)
async def update_car_availability(car_id: str, status: str = Query(...)):
    """Update car availability status (used by booking service)"""
    if status not in ['Available', 'Unavailable', 'Reserved']:
        raise HTTPException(status_code=400, detail="Invalid status. Must be: Available, Unavailable, or Reserved")
    
    success = CarRepository.update_availability_status(car_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Availability status updated successfully"}

@app.put("/cars/{car_id}/rating", status_code=200)
async def update_car_rating(car_id: str, new_rating: float = Query(..., ge=0, le=5), total_reviews: int = Query(..., ge=0)):
    """Update car rating (used by review service)"""
    success = CarRepository.update_rating(car_id, new_rating, total_reviews)
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Rating updated successfully"}

@app.on_event("startup")
async def startup_event():
    try:
        await KafkaProducerService.get_producer()
        print("Kafka producer initialized for Car Service")
    except Exception as e:
        print(f"Warning: Kafka producer initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await KafkaProducerService.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)

