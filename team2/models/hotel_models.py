"""
Hotel data models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

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

    @validator('state')
    def validate_state(cls, v):
        v = v.upper()
        valid_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                       'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                       'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                       'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                       'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']
        if v not in valid_states:
            raise ValueError(f'Invalid state abbreviation: {v}')
        return v

    class Config:
        json_schema_extra = {
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

    class Config:
        from_attributes = True

class HotelSearchParams(BaseModel):
    location: Optional[str] = None  # city or state
    city: Optional[str] = None
    state: Optional[str] = None
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_stars: Optional[int] = Field(None, ge=1, le=5)
    max_stars: Optional[int] = Field(None, ge=1, le=5)
    amenities: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class HotelSearchResponse(BaseModel):
    hotels: list[HotelResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

