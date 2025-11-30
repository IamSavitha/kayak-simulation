"""
Hotel API routes
"""
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.hotel_models import (
    HotelCreate, HotelUpdate, HotelResponse, HotelSearchParams, HotelSearchResponse
)
from repositories.hotel_repository import HotelRepository
from config.kafka_config import KafkaProducer
from datetime import datetime as dt

router = APIRouter(prefix="/hotels", tags=["hotels"])

@router.post("", response_model=HotelResponse, status_code=201)
async def create_hotel(hotel: HotelCreate):
    """Create a new hotel"""
    try:
        hotel_data = hotel.dict()
        created_hotel = HotelRepository.create(hotel_data)
        
        if not created_hotel:
            raise HTTPException(status_code=500, detail="Failed to create hotel")
        
        # Send Kafka event
        await KafkaProducer.send_listing_event(
            event_type="listing_created",
            listing_type="hotel",
            listing_id=created_hotel['hotel_id'],
            data={
                'hotel_name': created_hotel['hotel_name'],
                'city': created_hotel['city'],
                'state': created_hotel['state'],
                'price_per_night': float(created_hotel['price_per_night']),
                'star_rating': created_hotel['star_rating'],
                'timestamp': dt.utcnow().isoformat()
            }
        )
        
        return created_hotel
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: str):
    """Get hotel by ID"""
    hotel = HotelRepository.get_by_id(hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(hotel_id: str, hotel_update: HotelUpdate):
    """Update hotel"""
    existing = HotelRepository.get_by_id(hotel_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    update_data = hotel_update.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    updated_hotel = HotelRepository.update(hotel_id, update_data)
    
    if not updated_hotel:
        raise HTTPException(status_code=500, detail="Failed to update hotel")
    
    # Send Kafka event
    await KafkaProducer.send_listing_event(
        event_type="listing_updated",
        listing_type="hotel",
        listing_id=hotel_id,
        data={
            'updated_fields': list(update_data.keys()),
            'timestamp': dt.utcnow().isoformat()
        }
    )
    
    return updated_hotel

@router.delete("/{hotel_id}", status_code=204)
async def delete_hotel(hotel_id: str):
    """Delete hotel"""
    existing = HotelRepository.get_by_id(hotel_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    success = HotelRepository.delete(hotel_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete hotel")
    
    # Send Kafka event
    await KafkaProducer.send_listing_event(
        event_type="listing_deleted",
        listing_type="hotel",
        listing_id=hotel_id,
        data={'timestamp': dt.utcnow().isoformat()}
    )
    
    return None

@router.get("/search", response_model=HotelSearchResponse)
async def search_hotels(
    location: Optional[str] = Query(None, description="City or state"),
    city: Optional[str] = Query(None, description="City name"),
    state: Optional[str] = Query(None, description="State abbreviation"),
    check_in_date: Optional[datetime] = Query(None, description="Check-in date"),
    check_out_date: Optional[datetime] = Query(None, description="Check-out date"),
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
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'min_price': min_price,
        'max_price': max_price,
        'min_stars': min_stars,
        'max_stars': max_stars,
        'amenities': amenities_list,
        'page': page,
        'page_size': page_size
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    result = HotelRepository.search(search_params)
    
    return HotelSearchResponse(
        hotels=[HotelResponse(**h) for h in result['hotels']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )

@router.post("/{hotel_id}/images", status_code=201)
async def upload_hotel_image(
    hotel_id: str,
    image: UploadFile = File(...),
    image_type: str = Form(..., description="Image type: 'hotel' or 'room'")
):
    """Upload hotel image"""
    # Verify hotel exists
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

@router.get("/{hotel_id}/images", status_code=200)
async def get_hotel_images(hotel_id: str, image_type: Optional[str] = Query(None, description="Filter by image type")):
    """Get hotel images"""
    images = HotelRepository.get_images(hotel_id, image_type)
    return {"images": images}

@router.put("/{hotel_id}/availability", status_code=200)
async def update_hotel_availability(hotel_id: str, rooms_change: int = Query(..., description="Change in rooms (negative to decrease)")):
    """Update hotel availability (used by booking service)"""
    success = HotelRepository.update_availability(hotel_id, rooms_change)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update availability or insufficient rooms")
    return {"message": "Availability updated successfully"}

@router.put("/{hotel_id}/rating", status_code=200)
async def update_hotel_rating(hotel_id: str, new_rating: float = Query(..., ge=0, le=5), total_reviews: int = Query(..., ge=0)):
    """Update hotel rating (used by review service)"""
    success = HotelRepository.update_rating(hotel_id, new_rating, total_reviews)
    if not success:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"message": "Rating updated successfully"}

