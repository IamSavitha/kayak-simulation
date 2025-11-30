"""
Flight API routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.flight_models import (
    FlightCreate, FlightUpdate, FlightResponse, FlightSearchParams, FlightSearchResponse
)
from repositories.flight_repository import FlightRepository
from config.kafka_config import KafkaProducer
from datetime import datetime as dt

router = APIRouter(prefix="/flights", tags=["flights"])

@router.post("", response_model=FlightResponse, status_code=201)
async def create_flight(flight: FlightCreate):
    """Create a new flight"""
    try:
        flight_data = flight.dict()
        flight_data['departure_date_time'] = flight.departure_date_time
        flight_data['arrival_date_time'] = flight.arrival_date_time
        
        created_flight = FlightRepository.create(flight_data)
        
        if not created_flight:
            raise HTTPException(status_code=500, detail="Failed to create flight")
        
        # Send Kafka event
        await KafkaProducer.send_listing_event(
            event_type="listing_created",
            listing_type="flight",
            listing_id=created_flight['flight_id'],
            data={
                'airline': created_flight['airline'],
                'departure_airport': created_flight['departure_airport'],
                'arrival_airport': created_flight['arrival_airport'],
                'ticket_price': float(created_flight['ticket_price']),
                'timestamp': dt.utcnow().isoformat()
            }
        )
        
        return created_flight
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{flight_id}", response_model=FlightResponse)
async def get_flight(flight_id: str):
    """Get flight by ID"""
    flight = FlightRepository.get_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

@router.put("/{flight_id}", response_model=FlightResponse)
async def update_flight(flight_id: str, flight_update: FlightUpdate):
    """Update flight"""
    # Check if flight exists
    existing = FlightRepository.get_by_id(flight_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    update_data = flight_update.dict(exclude_unset=True)
    if not update_data:
        return existing
    
    updated_flight = FlightRepository.update(flight_id, update_data)
    
    if not updated_flight:
        raise HTTPException(status_code=500, detail="Failed to update flight")
    
    # Send Kafka event
    await KafkaProducer.send_listing_event(
        event_type="listing_updated",
        listing_type="flight",
        listing_id=flight_id,
        data={
            'updated_fields': list(update_data.keys()),
            'timestamp': dt.utcnow().isoformat()
        }
    )
    
    return updated_flight

@router.delete("/{flight_id}", status_code=204)
async def delete_flight(flight_id: str):
    """Delete flight"""
    # Check if flight exists
    existing = FlightRepository.get_by_id(flight_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    success = FlightRepository.delete(flight_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete flight")
    
    # Send Kafka event
    await KafkaProducer.send_listing_event(
        event_type="listing_deleted",
        listing_type="flight",
        listing_id=flight_id,
        data={'timestamp': dt.utcnow().isoformat()}
    )
    
    return None

@router.get("/search", response_model=FlightSearchResponse)
async def search_flights(
    origin: Optional[str] = Query(None, description="Departure airport code"),
    destination: Optional[str] = Query(None, description="Arrival airport code"),
    departure_date: Optional[datetime] = Query(None, description="Departure date"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    flight_class: Optional[str] = Query(None, description="Flight class: Economy, Business, First"),
    departure_time_start: Optional[str] = Query(None, description="Departure time start (HH:MM)"),
    departure_time_end: Optional[str] = Query(None, description="Departure time end (HH:MM)"),
    arrival_time_start: Optional[str] = Query(None, description="Arrival time start (HH:MM)"),
    arrival_time_end: Optional[str] = Query(None, description="Arrival time end (HH:MM)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """Search flights with filters"""
    search_params = {
        'origin': origin,
        'destination': destination,
        'departure_date': departure_date,
        'min_price': min_price,
        'max_price': max_price,
        'flight_class': flight_class,
        'departure_time_start': departure_time_start,
        'departure_time_end': departure_time_end,
        'arrival_time_start': arrival_time_start,
        'arrival_time_end': arrival_time_end,
        'page': page,
        'page_size': page_size
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    result = FlightRepository.search(search_params)
    
    return FlightSearchResponse(
        flights=[FlightResponse(**f) for f in result['flights']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )

@router.put("/{flight_id}/availability", status_code=200)
async def update_flight_availability(flight_id: str, seats_change: int = Query(..., description="Change in seats (negative to decrease)")):
    """Update flight availability (used by booking service)"""
    success = FlightRepository.update_availability(flight_id, seats_change)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update availability or insufficient seats")
    return {"message": "Availability updated successfully"}

@router.put("/{flight_id}/rating", status_code=200)
async def update_flight_rating(flight_id: str, new_rating: float = Query(..., ge=0, le=5), total_reviews: int = Query(..., ge=0)):
    """Update flight rating (used by review service)"""
    success = FlightRepository.update_rating(flight_id, new_rating, total_reviews)
    if not success:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"message": "Rating updated successfully"}

