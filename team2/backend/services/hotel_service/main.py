"""
Hotel Service - Port 8003
"""
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import uvicorn

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.schemas.hotel_schemas import (
    HotelCreate, HotelUpdate, HotelResponse, HotelSearchResponse
)
from backend.repositories.hotel_repository import HotelRepository
from backend.kafka.producer import KafkaProducerService
from backend.kafka.topics import EVENT_LISTING_CREATED, EVENT_LISTING_UPDATED, EVENT_LISTING_DELETED, LISTING_TYPE_HOTEL

app = FastAPI(
    title="Hotel Service",
    description="Team 2 - Hotel Listing Service",
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
    return {"service": "Hotel Service", "port": 8003, "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hotel-service"}

@app.post("/hotels", response_model=HotelResponse, status_code=201)
async def create_hotel(hotel: HotelCreate):
    """Create a new hotel"""
    try:
        hotel_data = hotel.model_dump()
        created_hotel = HotelRepository.create(hotel_data)
        
        if not created_hotel:
            raise HTTPException(status_code=500, detail="Failed to create hotel")
        
        await KafkaProducerService.send_listing_event(
            event_type=EVENT_LISTING_CREATED,
            listing_type=LISTING_TYPE_HOTEL,
            listing_id=created_hotel['hotel_id'],
            data={
                'hotel_name': created_hotel['hotel_name'],
                'city': created_hotel['city'],
                'state': created_hotel['state'],
                'price_per_night': float(created_hotel['price_per_night']),
                'star_rating': created_hotel['star_rating'],
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return created_hotel
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/hotels/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: str):
    """Get hotel by ID"""
    hotel = HotelRepository.get_by_id(hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@app.put("/hotels/{hotel_id}", response_model=HotelResponse)
async def update_hotel(hotel_id: str, hotel_update: HotelUpdate):
    """Update hotel"""
    existing = HotelRepository.get_by_id(hotel_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    update_data = hotel_update.model_dump(exclude_unset=True)
    if not update_data:
        return existing
    
    updated_hotel = HotelRepository.update(hotel_id, update_data)
    
    if not updated_hotel:
        raise HTTPException(status_code=500, detail="Failed to update hotel")
    
    await KafkaProducerService.send_listing_event(
        event_type=EVENT_LISTING_UPDATED,
        listing_type=LISTING_TYPE_HOTEL,
        listing_id=hotel_id,
        data={
            'updated_fields': list(update_data.keys()),
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    return updated_hotel

@app.delete("/hotels/{hotel_id}", status_code=204)
async def delete_hotel(hotel_id: str):
    """Delete hotel"""
    existing = HotelRepository.get_by_id(hotel_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    success = HotelRepository.delete(hotel_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete hotel")
    
    await KafkaProducerService.send_listing_event(
        event_type=EVENT_LISTING_DELETED,
        listing_type=LISTING_TYPE_HOTEL,
        listing_id=hotel_id,
        data={'timestamp': datetime.utcnow().isoformat()}
    )
    
    return None

@app.get("/hotels/search", response_model=HotelSearchResponse)
async def search_hotels(
    location: Optional[str] = Query(None, description="City or state"),
    city: Optional[str] = Query(None, description="City name"),
    state: Optional[str] = Query(None, description="State abbreviation"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price per night"),
    min_stars: Optional[int] = Query(None, ge=1, le=5, description="Minimum star rating"),
    max_stars: Optional[int] = Query(None, ge=1, le=5, description="Maximum star rating"),
    amenities: Optional[str] = Query(None, description="Comma-separated amenities"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """Search hotels with filters"""
    amenities_list = None
    if amenities:
        amenities_list = [a.strip() for a in amenities.split(',')]
    
    search_params = {
        'location': location,
        'city': city,
        'state': state,
        'min_price': min_price,
        'max_price': max_price,
        'min_stars': min_stars,
        'max_stars': max_stars,
        'amenities': amenities_list,
        'page': page,
        'page_size': page_size
    }
    
    search_params = {k: v for k, v in search_params.items() if v is not None}
    result = HotelRepository.search(search_params)
    
    return HotelSearchResponse(
        hotels=[HotelResponse(**h) for h in result['hotels']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )

@app.post("/hotels/{hotel_id}/images", status_code=201)
async def upload_hotel_image(
    hotel_id: str,
    image: UploadFile = File(...),
    image_type: str = Form(..., description="Image type: 'hotel' or 'room'")
):
    """Upload hotel image"""
    hotel = HotelRepository.get_by_id(hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    if image_type not in ['hotel', 'room']:
        raise HTTPException(status_code=400, detail="image_type must be 'hotel' or 'room'")
    
    image_data = await image.read()
    metadata = {
        'filename': image.filename,
        'content_type': image.content_type,
        'size': len(image_data)
    }
    
    image_id = HotelRepository.save_image(hotel_id, image_type, image_data, metadata)
    return {"image_id": image_id, "message": "Image uploaded successfully"}

@app.get("/hotels/{hotel_id}/images", status_code=200)
async def get_hotel_images(hotel_id: str, image_type: Optional[str] = Query(None)):
    """Get hotel images"""
    images = HotelRepository.get_images(hotel_id, image_type)
    return {"images": images}

@app.put("/hotels/{hotel_id}/availability", status_code=200)
async def update_hotel_availability(hotel_id: str, rooms_change: int = Query(...)):
    """Update hotel availability (used by booking service)"""
    success = HotelRepository.update_availability(hotel_id, rooms_change)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update availability or insufficient rooms")
    return {"message": "Availability updated successfully"}

@app.put("/hotels/{hotel_id}/rating", status_code=200)
async def update_hotel_rating(hotel_id: str, new_rating: float = Query(..., ge=0, le=5), total_reviews: int = Query(..., ge=0)):
    """Update hotel rating (used by review service)"""
    success = HotelRepository.update_rating(hotel_id, new_rating, total_reviews)
    if not success:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"message": "Rating updated successfully"}

@app.on_event("startup")
async def startup_event():
    try:
        await KafkaProducerService.get_producer()
        print("Kafka producer initialized for Hotel Service")
    except Exception as e:
        print(f"Warning: Kafka producer initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await KafkaProducerService.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

