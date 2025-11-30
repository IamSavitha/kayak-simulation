"""
Hotel Pydantic schemas - Team 5 compatible
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from backend.common.validators import VALID_STATES

class HotelCreate(BaseModel):
    hotel_name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., min_length=5, max_length=10)
    star_rating: int = Field(..., ge=1, le=5)
    number_of_rooms: int = Field(..., ge=0)
    current_available_rooms: Optional[int] = None
    room_type: str = Field(..., min_length=1, max_length=50)
    price_per_night: float = Field(..., gt=0)
    amenities: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        v = v.upper()
        if v not in VALID_STATES:
            raise ValueError(f'Invalid state abbreviation: {v}')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "hotel_name": "Grand Hotel",
                "address": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "star_rating": 4,
                "number_of_rooms": 100,
                "current_available_rooms": 50,
                "room_type": "Deluxe",
                "price_per_night": 199.99,
                "amenities": "Wi-Fi, Breakfast, Parking, Pool",
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
    }

class HotelUpdate(BaseModel):
    hotel_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    star_rating: Optional[int] = None
    number_of_rooms: Optional[int] = None
    current_available_rooms: Optional[int] = None
    room_type: Optional[str] = None
    price_per_night: Optional[float] = None
    amenities: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HotelResponse(BaseModel):
    hotel_id: str
    hotel_name: str
    address: str
    city: str
    state: str
    zip_code: str
    star_rating: int
    number_of_rooms: int
    current_available_rooms: int
    room_type: str
    price_per_night: float
    amenities: Optional[str]
    hotel_rating: float
    total_reviews: int
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class HotelSearchResponse(BaseModel):
    hotels: List[HotelResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

