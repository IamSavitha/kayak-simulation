"""
Hotel Service - FastAPI application for hotel management.
"""
from fastapi import FastAPI, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import logging

from ...common.config import settings
from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found
from ...schemas.hotel_schemas import (
    HotelCreate, HotelUpdate, HotelResponse,
    HotelSearchParams, HotelSearchResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kayak Hotel Service",
    description="Hotel search and booking microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Hotel Service...")
    init_mysql_db()


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    return await get_comprehensive_health(
        check_mysql=True,
        check_redis=True,
        service_name="hotel-service"
    )


@app.post("/hotels", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
async def create_hotel(hotel_data: HotelCreate, db: Session = Depends(get_mysql_session)):
    """Create a new hotel listing."""
    from .service import HotelService
    service = HotelService(db)
    return service.create_hotel(hotel_data)


@app.get("/hotels/search", response_model=HotelSearchResponse)
async def search_hotels(
    city: Optional[str] = None,
    state: Optional[str] = None,
    check_in_date: Optional[date] = None,
    check_out_date: Optional[date] = None,
    min_star_rating: Optional[int] = Query(None, ge=1, le=5),
    max_star_rating: Optional[int] = Query(None, ge=1, le=5),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    amenities: Optional[str] = None,
    num_rooms: int = Query(default=1, ge=1),
    num_guests: int = Query(default=2, ge=1),
    sort_by: str = Query(default="price"),
    sort_order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=1000),
    db: Session = Depends(get_mysql_session)
):
    """Search for hotels with filters."""
    from .service import HotelService
    from decimal import Decimal
    
    service = HotelService(db)
    params = HotelSearchParams(
        city=city, state=state,
        check_in_date=check_in_date, check_out_date=check_out_date,
        min_star_rating=min_star_rating, max_star_rating=max_star_rating,
        min_price=Decimal(str(min_price)) if min_price else None,
        max_price=Decimal(str(max_price)) if max_price else None,
        amenities=amenities.split(',') if amenities else None,
        num_rooms=num_rooms, num_guests=num_guests,
        sort_by=sort_by, sort_order=sort_order,
        page=page, page_size=page_size
    )
    return service.search_hotels(params)


@app.get("/hotels/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: str, db: Session = Depends(get_mysql_session)):
    """Get hotel by ID."""
    from .service import HotelService
    service = HotelService(db)
    hotel = service.get_hotel(hotel_id)
    if not hotel:
        handle_not_found("Hotel", hotel_id)
    return hotel


@app.put("/hotels/{hotel_id}", response_model=HotelResponse)
async def update_hotel(hotel_id: str, hotel_data: HotelUpdate, db: Session = Depends(get_mysql_session)):
    """Update hotel information."""
    from .service import HotelService
    service = HotelService(db)
    hotel = service.update_hotel(hotel_id, hotel_data)
    if not hotel:
        handle_not_found("Hotel", hotel_id)
    return hotel


@app.delete("/hotels/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hotel(hotel_id: str, db: Session = Depends(get_mysql_session)):
    """Delete a hotel listing."""
    from .service import HotelService
    service = HotelService(db)
    if not service.delete_hotel(hotel_id):
        handle_not_found("Hotel", hotel_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

