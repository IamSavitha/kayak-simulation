"""
Hotel Service - Business logic for hotel operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime
import math
import logging

from ...models.mysql_models import Hotel, HotelRoom, Booking, BookingType, BookingStatus
from ...schemas.hotel_schemas import (
    HotelCreate, HotelUpdate, HotelSearchParams, 
    HotelSearchResponse, HotelResponse
)
from ...common.cache import RedisCache, CacheKeys

logger = logging.getLogger(__name__)


class HotelService:
    """Service class for hotel operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = RedisCache()
    
    def create_hotel(self, hotel_data: HotelCreate) -> Hotel:
        """Create a new hotel."""
        hotel = Hotel(
            hotel_id=hotel_data.hotel_id,
            hotel_name=hotel_data.hotel_name,
            description=hotel_data.description,
            address=hotel_data.address,
            city=hotel_data.city,
            state=hotel_data.state,
            zip_code=hotel_data.zip_code,
            star_rating=hotel_data.star_rating,
            amenities=hotel_data.amenities,
            phone_number=hotel_data.phone_number,
            email=hotel_data.email,
            website=hotel_data.website,
            image_url=hotel_data.image_url
        )
        
        self.db.add(hotel)
        self.db.commit()
        self.db.refresh(hotel)
        
        logger.info(f"Created hotel: {hotel.hotel_id}")
        return hotel
    
    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """Get hotel by ID."""
        return self.db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
    
    def update_hotel(self, hotel_id: str, hotel_data: HotelUpdate) -> Optional[Hotel]:
        """Update hotel information."""
        hotel = self.db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            return None
        
        update_data = hotel_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(hotel, field):
                setattr(hotel, field, value)
        
        self.db.commit()
        self.db.refresh(hotel)
        self.cache.delete(CacheKeys.hotel(hotel_id))
        
        return hotel
    
    def delete_hotel(self, hotel_id: str) -> bool:
        """Delete a hotel (soft delete)."""
        hotel = self.db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            return False
        
        hotel.is_active = False
        self.db.commit()
        self.cache.delete(CacheKeys.hotel(hotel_id))
        
        return True
    
    def search_hotels(self, params: HotelSearchParams) -> HotelSearchResponse:
        """Search hotels with filters."""
        query = self.db.query(Hotel).filter(Hotel.is_active == True)
        
        if params.city:
            query = query.filter(Hotel.city.ilike(f"%{params.city}%"))
        
        if params.state:
            query = query.filter(Hotel.state == params.state.upper())
        
        if params.min_star_rating:
            query = query.filter(Hotel.star_rating >= params.min_star_rating)
        
        if params.max_star_rating:
            query = query.filter(Hotel.star_rating <= params.max_star_rating)
        
        if params.amenities:
            for amenity in params.amenities:
                query = query.filter(Hotel.amenities.ilike(f"%{amenity}%"))
        
        total_count = query.count()
        
        # Sorting
        if params.sort_by == "rating":
            order_col = Hotel.rating
        elif params.sort_by == "stars":
            order_col = Hotel.star_rating
        else:
            order_col = Hotel.hotel_name
        
        if params.sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
        
        offset = (params.page - 1) * params.page_size
        hotels = query.offset(offset).limit(params.page_size).all()
        
        # Calculate available rooms for each hotel
        hotel_responses = []
        for hotel in hotels:
            hotel_dict = HotelResponse.model_validate(hotel).model_dump()
            
            # Get total available rooms for this hotel
            total_available_rooms = self.db.query(func.sum(HotelRoom.available_rooms)).filter(
                HotelRoom.hotel_id == hotel.hotel_id,
                HotelRoom.is_active == True
            ).scalar() or 0
            
            # Check date availability if dates are provided
            if params.check_in_date and params.check_out_date:
                # Count overlapping bookings for the requested dates
                overlapping_bookings = self.db.query(func.sum(Booking.num_rooms)).filter(
                    Booking.listing_id == hotel.hotel_id,
                    Booking.booking_type == BookingType.HOTEL.value,
                    Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
                    or_(
                        and_(
                            Booking.check_in_date <= params.check_in_date,
                            Booking.check_out_date > params.check_in_date
                        ),
                        and_(
                            Booking.check_in_date < params.check_out_date,
                            Booking.check_out_date >= params.check_out_date
                        ),
                        and_(
                            Booking.check_in_date >= params.check_in_date,
                            Booking.check_out_date <= params.check_out_date
                        )
                    )
                ).scalar() or 0
                
                # Available rooms = total available - booked rooms
                available_for_dates = max(0, int(total_available_rooms) - int(overlapping_bookings))
            else:
                available_for_dates = int(total_available_rooms)
            
            hotel_dict['available_rooms'] = available_for_dates
            hotel_dict['total_available_rooms'] = int(total_available_rooms)
            hotel_responses.append(hotel_dict)
        
        return HotelSearchResponse(
            hotels=hotel_responses,
            total_count=total_count,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total_count / params.page_size) if total_count > 0 else 1,
            filters_applied=params.model_dump(exclude_none=True)
        )
    
    def get_hotel_rooms(self, hotel_id: str) -> List[HotelRoom]:
        """Get all rooms for a hotel."""
        return self.db.query(HotelRoom).filter(
            HotelRoom.hotel_id == hotel_id,
            HotelRoom.is_active == True
        ).all()
    
    def check_room_availability(
        self,
        hotel_id: str,
        room_type: Optional[str] = None,
        check_in: datetime = None,
        check_out: datetime = None,
        num_rooms: int = 1
    ) -> dict:
        """Check room availability for a hotel."""
        rooms_query = self.db.query(HotelRoom).filter(
            HotelRoom.hotel_id == hotel_id,
            HotelRoom.is_active == True
        )
        
        if room_type:
            rooms_query = rooms_query.filter(HotelRoom.room_type == room_type)
        
        rooms = rooms_query.all()
        
        available_rooms = []
        for room in rooms:
            # Check if enough rooms are available
            if room.available_rooms >= num_rooms:
                # If dates provided, check for overlapping bookings
                if check_in and check_out:
                    from ...models.mysql_models import Booking, BookingType, BookingStatus
                    overlapping = self.db.query(Booking).filter(
                        and_(
                            Booking.listing_id == hotel_id,
                            Booking.booking_type == BookingType.HOTEL,
                            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                            or_(
                                and_(
                                    Booking.check_in_date <= check_in,
                                    Booking.check_out_date > check_in
                                ),
                                and_(
                                    Booking.check_in_date < check_out,
                                    Booking.check_out_date >= check_out
                                )
                            )
                        )
                    ).count()
                    
                    if overlapping == 0:
                        available_rooms.append({
                            "room_id": room.room_id,
                            "room_type": room.room_type.value if hasattr(room.room_type, 'value') else str(room.room_type),
                            "price_per_night": float(room.price_per_night),
                            "available_rooms": room.available_rooms,
                            "max_occupancy": room.max_occupancy
                        })
                else:
                    available_rooms.append({
                        "room_id": room.room_id,
                        "room_type": room.room_type.value if hasattr(room.room_type, 'value') else str(room.room_type),
                        "price_per_night": float(room.price_per_night),
                        "available_rooms": room.available_rooms,
                        "max_occupancy": room.max_occupancy
                    })
        
        return {
            "hotel_id": hotel_id,
            "check_in": str(check_in) if check_in else None,
            "check_out": str(check_out) if check_out else None,
            "available_rooms": available_rooms,
            "total_available": len(available_rooms)
        }
    
    def calculate_hotel_price(
        self,
        hotel_id: str,
        room_type: str,
        check_in: datetime,
        check_out: datetime,
        num_rooms: int = 1
    ) -> dict:
        """Calculate hotel booking price."""
        room = self.db.query(HotelRoom).filter(
            HotelRoom.hotel_id == hotel_id,
            HotelRoom.room_type == room_type,
            HotelRoom.is_active == True
        ).first()
        
        if not room:
            raise ValueError(f"Room type {room_type} not found for hotel {hotel_id}")
        
        # Calculate number of nights
        delta = check_out - check_in
        num_nights = max(1, delta.days)
        
        # Calculate price
        from decimal import Decimal
        price_per_night = Decimal(str(room.price_per_night))
        total_price = price_per_night * Decimal(num_nights) * Decimal(num_rooms)
        
        return {
            "price_per_night": float(price_per_night),
            "num_nights": num_nights,
            "num_rooms": num_rooms,
            "subtotal": float(total_price),
            "total_price": float(total_price)
        }


