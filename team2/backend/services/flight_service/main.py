"""
Flight Service - Port 8002
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import uvicorn

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.schemas.flight_schemas import (
    FlightCreate, FlightUpdate, FlightResponse, FlightSearchResponse
)
from backend.repositories.flight_repository import FlightRepository
from backend.kafka.producer import KafkaProducerService
from backend.kafka.topics import EVENT_LISTING_CREATED, EVENT_LISTING_UPDATED, EVENT_LISTING_DELETED, LISTING_TYPE_FLIGHT

app = FastAPI(
    title="Flight Service",
    description="Team 2 - Flight Listing Service",
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
    return {"service": "Flight Service", "port": 8002, "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "flight-service"}

@app.post("/flights", response_model=FlightResponse, status_code=201)
async def create_flight(flight: FlightCreate):
    """Create a new flight"""
    try:
        flight_data = flight.model_dump()
        created_flight = FlightRepository.create(flight_data)
        
        if not created_flight:
            raise HTTPException(status_code=500, detail="Failed to create flight")
        
        await KafkaProducerService.send_listing_event(
            event_type=EVENT_LISTING_CREATED,
            listing_type=LISTING_TYPE_FLIGHT,
            listing_id=created_flight['flight_id'],
            data={
                'airline': created_flight['airline'],
                'departure_airport': created_flight['departure_airport'],
                'arrival_airport': created_flight['arrival_airport'],
                'ticket_price': float(created_flight['ticket_price']),
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return created_flight
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/flights/{flight_id}", response_model=FlightResponse)
async def get_flight(flight_id: str):
    """Get flight by ID"""
    flight = FlightRepository.get_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

@app.put("/flights/{flight_id}", response_model=FlightResponse)
async def update_flight(flight_id: str, flight_update: FlightUpdate):
    """Update flight"""
    existing = FlightRepository.get_by_id(flight_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    update_data = flight_update.model_dump(exclude_unset=True)
    if not update_data:
        return existing
    
    updated_flight = FlightRepository.update(flight_id, update_data)
    
    if not updated_flight:
        raise HTTPException(status_code=500, detail="Failed to update flight")
    
    await KafkaProducerService.send_listing_event(
        event_type=EVENT_LISTING_UPDATED,
        listing_type=LISTING_TYPE_FLIGHT,
        listing_id=flight_id,
        data={
            'updated_fields': list(update_data.keys()),
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    return updated_flight

@app.delete("/flights/{flight_id}", status_code=204)
async def delete_flight(flight_id: str):
    """Delete flight"""
    existing = FlightRepository.get_by_id(flight_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    success = FlightRepository.delete(flight_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete flight")
    
    await KafkaProducerService.send_listing_event(
        event_type=EVENT_LISTING_DELETED,
        listing_type=LISTING_TYPE_FLIGHT,
        listing_id=flight_id,
        data={'timestamp': datetime.utcnow().isoformat()}
    )
    
    return None

@app.get("/flights/search", response_model=FlightSearchResponse)
async def search_flights(
    origin: Optional[str] = Query(None, description="Departure airport code"),
    destination: Optional[str] = Query(None, description="Arrival airport code"),
    departure_date: Optional[datetime] = Query(None, description="Departure date"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    flight_class: Optional[str] = Query(None, description="Flight class: Economy, Business, First"),
    departure_time_start: Optional[str] = Query(None, description="Departure time start (HH:MM)"),
    departure_time_end: Optional[str] = Query(None, description="Departure time end (HH:MM)"),
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
        'page': page,
        'page_size': page_size
    }
    
    search_params = {k: v for k, v in search_params.items() if v is not None}
    result = FlightRepository.search(search_params)
    
    return FlightSearchResponse(
        flights=[FlightResponse(**f) for f in result['flights']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )

@app.put("/flights/{flight_id}/availability", status_code=200)
async def update_flight_availability(flight_id: str, seats_change: int = Query(...)):
    """Update flight availability (used by booking service)"""
    success = FlightRepository.update_availability(flight_id, seats_change)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update availability or insufficient seats")
    return {"message": "Availability updated successfully"}

@app.put("/flights/{flight_id}/rating", status_code=200)
async def update_flight_rating(flight_id: str, new_rating: float = Query(..., ge=0, le=5), total_reviews: int = Query(..., ge=0)):
    """Update flight rating (used by review service)"""
    success = FlightRepository.update_rating(flight_id, new_rating, total_reviews)
    if not success:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"message": "Rating updated successfully"}

@app.on_event("startup")
async def startup_event():
    try:
        await KafkaProducerService.get_producer()
        print("Kafka producer initialized for Flight Service")
    except Exception as e:
        print(f"Warning: Kafka producer initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await KafkaProducerService.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

