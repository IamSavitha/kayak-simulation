"""
Car Pydantic schemas - Team 5 compatible
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransmissionType(str, Enum):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"

class AvailabilityStatus(str, Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    RESERVED = "Reserved"

class CarCreate(BaseModel):
    car_type: str = Field(..., min_length=1, max_length=50)
    company_provider_name: str = Field(..., min_length=1, max_length=100)
    model_and_year: str = Field(..., min_length=1, max_length=100)
    transmission_type: TransmissionType = TransmissionType.AUTOMATIC
    number_of_seats: int = Field(..., ge=2, le=8)
    daily_rental_price: float = Field(..., gt=0)
    availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_address: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "car_type": "SUV",
                "company_provider_name": "Hertz",
                "model_and_year": "Toyota RAV4 2023",
                "transmission_type": "Automatic",
                "number_of_seats": 5,
                "daily_rental_price": 89.99,
                "availability_status": "Available",
                "location_city": "New York",
                "location_state": "NY",
                "location_address": "123 Car Rental St"
            }
        }
    }

class CarUpdate(BaseModel):
    car_type: Optional[str] = None
    company_provider_name: Optional[str] = None
    model_and_year: Optional[str] = None
    transmission_type: Optional[TransmissionType] = None
    number_of_seats: Optional[int] = None
    daily_rental_price: Optional[float] = None
    availability_status: Optional[AvailabilityStatus] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_address: Optional[str] = None

class CarResponse(BaseModel):
    car_id: str
    car_type: str
    company_provider_name: str
    model_and_year: str
    transmission_type: str
    number_of_seats: int
    daily_rental_price: float
    car_rating: float
    total_reviews: int
    availability_status: str
    location_city: Optional[str]
    location_state: Optional[str]
    location_address: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CarSearchResponse(BaseModel):
    cars: List[CarResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

