"""
Car API routes
"""
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.car_models import (
    CarCreate, CarUpdate, CarResponse, CarSearchParams, CarSearchResponse
)
from repositories.car_repository import CarRepository
from config.kafka_config import KafkaProducer
from datetime import datetime as dt

router = APIRouter(prefix="/cars", tags=["cars"])

@router.post("", response_model=CarResponse, status_code=201)
async def create_car(car: CarCreate):
    """Create a new car listing"""
    try:
        car_data = car.dict()
        created_car = CarRepository.create(car_data)
        
        if not created_car:
            raise HTTPException(status_code=500, detail="Failed to create car")
        
        # Send Kafka event
        await KafkaProducer.send_listing_event(
            event_type="listing_created",
            listing_type="car",
            listing_id=created_car['car_id'],
            data={
                'car_type': created_car['car_type'],
                'company_provider_name': created_car['company_provider_name'],
                'daily_rental_price': float(created_car['daily_rental_price']),
                'location_city': created_car.get('location_city'),
                'location_state': created_car.get('location_state'),
                'timestamp': dt.utcnow().isoformat()
            }
        )
        
        return created_car
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{car_id}", response_model=CarResponse)
async def get_car(car_id: str):
    """Get car by ID"""
    car = CarRepository.get_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@router.put("/{car_id}", response_model=CarResponse)
async def update_car(car_id: str, car_update: CarUpdate):
    """Update car"""
    existing = CarRepository.get_by_id(car_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Car not found")
    
    update_data = car_update.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    updated_car = CarRepository.update(car_id, update_data)
    
    if not updated_car:
        raise HTTPException(status_code=500, detail="Failed to update car")
    
    # Send Kafka event
    await KafkaProducer.send_listing_event(
        event_type="listing_updated",
        listing_type="car",
        listing_id=car_id,
        data={
            'updated_fields': list(update_data.keys()),
            'timestamp': dt.utcnow().isoformat()
        }
    )
    
    return updated_car

@router.delete("/{car_id}", status_code=204)
async def delete_car(car_id: str):
    """Delete car"""
    existing = CarRepository.get_by_id(car_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Car not found")
    
    success = CarRepository.delete(car_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete car")
    
    # Send Kafka event
    await KafkaProducer.send_listing_event(
        event_type="listing_deleted",
        listing_type="car",
        listing_id=car_id,
        data={'timestamp': dt.utcnow().isoformat()}
    )
    
    return None

@router.get("/search", response_model=CarSearchResponse)
async def search_cars(
    location: Optional[str] = Query(None, description="City or state"),
    city: Optional[str] = Query(None, description="City name"),
    state: Optional[str] = Query(None, description="State abbreviation"),
    car_type: Optional[str] = Query(None, description="Car type (SUV, Sedan, Compact, etc.)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum daily rental price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum daily rental price"),
    transmission_type: Optional[str] = Query(None, description="Transmission type: Automatic or Manual"),
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
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    result = CarRepository.search(search_params)
    
    return CarSearchResponse(
        cars=[CarResponse(**c) for c in result['cars']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )

@router.post("/{car_id}/images", status_code=201)
async def upload_car_image(car_id: str, image: UploadFile = File(...)):
    """Upload car image"""
    # Verify car exists
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

@router.get("/{car_id}/images", status_code=200)
async def get_car_images(car_id: str):
    """Get car images"""
    images = CarRepository.get_images(car_id)
    return {"images": images}

@router.put("/{car_id}/availability", status_code=200)
async def update_car_availability(car_id: str, status: str = Query(..., description="Availability status: Available, Unavailable, Reserved")):
    """Update car availability status (used by booking service)"""
    if status not in ['Available', 'Unavailable', 'Reserved']:
        raise HTTPException(status_code=400, detail="Invalid status. Must be: Available, Unavailable, or Reserved")
    
    success = CarRepository.update_availability_status(car_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Availability status updated successfully"}

@router.put("/{car_id}/rating", status_code=200)
async def update_car_rating(car_id: str, new_rating: float = Query(..., ge=0, le=5), total_reviews: int = Query(..., ge=0)):
    """Update car rating (used by review service)"""
    success = CarRepository.update_rating(car_id, new_rating, total_reviews)
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Rating updated successfully"}

