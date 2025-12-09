"""
Pydantic schemas for Car rental requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class CarType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    COMPACT = "compact"
    LUXURY = "luxury"
    VAN = "van"


class TransmissionType(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class CarBase(BaseModel):
    """Base car schema."""
    car_type: CarType
    make: str = Field(..., max_length=50)
    model: str = Field(..., max_length=50)
    year: int = Field(..., ge=1990, le=2030)
    provider_name: str = Field(..., max_length=100)
    transmission_type: TransmissionType = TransmissionType.AUTOMATIC
    seats: int = Field(..., ge=2, le=15)
    doors: int = Field(default=4, ge=2, le=6)
    daily_rental_price: Decimal = Field(..., gt=0)
    pickup_location: str = Field(..., max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    image_url: Optional[str] = Field(None, max_length=500, description="URL to car image")


class CarCreate(CarBase):
    """Schema for creating a new car listing."""
    car_id: str = Field(..., max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "car_id": "CAR-001",
                "car_type": "suv",
                "make": "Toyota",
                "model": "RAV4",
                "year": 2024,
                "provider_name": "Enterprise",
                "transmission_type": "automatic",
                "seats": 5,
                "doors": 4,
                "daily_rental_price": 89.99,
                "pickup_location": "SFO Airport",
                "city": "San Francisco",
                "state": "CA"
            }
        }


class CarUpdate(BaseModel):
    """Schema for updating car information."""
    car_type: Optional[CarType] = None
    make: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1990, le=2030)
    provider_name: Optional[str] = Field(None, max_length=100)
    transmission_type: Optional[TransmissionType] = None
    seats: Optional[int] = Field(None, ge=2, le=15)
    doors: Optional[int] = Field(None, ge=2, le=6)
    daily_rental_price: Optional[Decimal] = Field(None, gt=0)
    pickup_location: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    image_url: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None


class CarResponse(BaseModel):
    """Schema for car response."""
    car_id: str
    car_type: str
    make: str
    model: str
    year: int
    provider_name: str
    transmission_type: str
    seats: int
    doors: int
    daily_rental_price: Decimal
    pickup_location: str
    city: Optional[str] = None
    state: Optional[str] = None
    image_url: Optional[str] = None
    rating: float = 0.0
    total_reviews: int = 0
    is_available: bool = True
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CarSearchParams(BaseModel):
    """Schema for car search parameters."""
    city: Optional[str] = None
    state: Optional[str] = None
    pickup_date: Optional[date] = None
    return_date: Optional[date] = None
    car_type: Optional[CarType] = None
    transmission_type: Optional[TransmissionType] = None
    min_seats: Optional[int] = Field(None, ge=2)
    provider_name: Optional[str] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    sort_by: Optional[str] = Field(default="price", description="price, rating, type")
    sort_order: Optional[str] = Field(default="asc", description="asc or desc")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=1000)


class CarSearchResponse(BaseModel):
    """Schema for car search results."""
    cars: List[CarResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: dict = {}

