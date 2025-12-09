"""
Pydantic schemas for Hotel-related requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
    DELUXE = "deluxe"


class HotelBase(BaseModel):
    """Base hotel schema."""
    hotel_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    star_rating: Optional[int] = Field(None, ge=1, le=5)
    amenities: Optional[str] = Field(None, description="Comma-separated amenities")
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=500, description="URL to hotel image")


class HotelCreate(HotelBase):
    """Schema for creating a new hotel."""
    hotel_id: str = Field(..., max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "hotel_id": "HOTEL-001",
                "hotel_name": "Grand Plaza Hotel",
                "description": "Luxury hotel in downtown",
                "address": "100 Market St",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94105",
                "star_rating": 4,
                "amenities": "wifi,breakfast,parking,pool,gym",
                "phone_number": "415-555-0100",
                "email": "info@grandplaza.com"
            }
        }


class HotelUpdate(BaseModel):
    """Schema for updating hotel information."""
    hotel_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    star_rating: Optional[int] = Field(None, ge=1, le=5)
    amenities: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class HotelRoomCreate(BaseModel):
    """Schema for creating a hotel room."""
    room_id: str = Field(..., max_length=50)
    room_type: RoomType
    room_number: Optional[str] = Field(None, max_length=10)
    price_per_night: Decimal = Field(..., gt=0)
    max_occupancy: int = Field(default=2, ge=1)
    total_rooms: int = Field(default=1, ge=1)


class HotelRoomUpdate(BaseModel):
    """Schema for updating a hotel room."""
    price_per_night: Optional[Decimal] = Field(None, gt=0)
    max_occupancy: Optional[int] = Field(None, ge=1)
    total_rooms: Optional[int] = Field(None, ge=1)
    available_rooms: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


# Alias for backward compatibility
HotelRoomUpdateData = HotelRoomUpdate


class HotelRoomResponse(BaseModel):
    """Schema for hotel room response."""
    room_id: str
    hotel_id: str
    room_type: str
    room_number: Optional[str] = None
    price_per_night: Decimal
    max_occupancy: int
    total_rooms: int
    available_rooms: int
    is_active: bool = True

    class Config:
        from_attributes = True


class HotelResponse(BaseModel):
    """Schema for hotel response."""
    hotel_id: str
    hotel_name: str
    description: Optional[str] = None
    address: str
    city: str
    state: Optional[str] = None
    zip_code: Optional[str] = None
    star_rating: Optional[int] = None
    rating: float = 0.0
    total_reviews: int = 0
    amenities: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    rooms: Optional[List[HotelRoomResponse]] = None
    available_rooms: Optional[int] = None  # Available rooms for selected dates
    total_available_rooms: Optional[int] = None  # Total available rooms
    min_price: Optional[float] = None  # Minimum room price per night
    
    class Config:
        from_attributes = True


class HotelSearchParams(BaseModel):
    """Schema for hotel search parameters."""
    city: Optional[str] = None
    state: Optional[str] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    room_type: Optional[RoomType] = None
    min_star_rating: Optional[int] = Field(None, ge=1, le=5)
    max_star_rating: Optional[int] = Field(None, ge=1, le=5)
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    amenities: Optional[List[str]] = Field(None, description="List of required amenities")
    num_rooms: int = Field(default=1, ge=1, le=10)
    num_guests: int = Field(default=2, ge=1, le=20)
    sort_by: Optional[str] = Field(default="price", description="price, rating, stars")
    sort_order: Optional[str] = Field(default="asc", description="asc or desc")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=1000)


class HotelSearchResponse(BaseModel):
    """Schema for hotel search results."""
    hotels: List[HotelResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: dict = {}

