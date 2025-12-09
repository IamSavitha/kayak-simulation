"""
Pydantic schemas for Flight-related requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class FlightClass(str, Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"


class FlightBase(BaseModel):
    """Base flight schema."""
    airline_name: str = Field(..., max_length=100)
    operator_name: Optional[str] = Field(None, max_length=100)
    departure_airport: str = Field(..., min_length=3, max_length=5)
    arrival_airport: str = Field(..., min_length=3, max_length=5)
    departure_datetime: datetime
    arrival_datetime: datetime
    flight_class: FlightClass = FlightClass.ECONOMY
    base_price: Decimal = Field(..., gt=0)
    total_seats: int = Field(..., gt=0)
    
    @field_validator('departure_airport', 'arrival_airport')
    @classmethod
    def uppercase_airport(cls, v):
        return v.upper()


class FlightCreate(FlightBase):
    """Schema for creating a new flight."""
    flight_id: str = Field(..., max_length=10, description="Flight ID (e.g., AA123)")
    available_seats: Optional[int] = None
    
    @field_validator('flight_id')
    @classmethod
    def validate_flight_id(cls, v):
        import re
        if not re.match(r'^[A-Z]{2}[0-9]{1,4}$', v.upper()):
            raise ValueError('Flight ID must be in format: AA123')
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "flight_id": "AA123",
                "airline_name": "American Airlines",
                "departure_airport": "SFO",
                "arrival_airport": "JFK",
                "departure_datetime": "2025-12-01T08:00:00",
                "arrival_datetime": "2025-12-01T16:30:00",
                "flight_class": "economy",
                "base_price": 299.99,
                "total_seats": 180
            }
        }


class FlightUpdate(BaseModel):
    """Schema for updating flight information."""
    airline_name: Optional[str] = Field(None, max_length=100)
    operator_name: Optional[str] = Field(None, max_length=100)
    departure_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None
    base_price: Optional[Decimal] = Field(None, gt=0)
    available_seats: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class FlightResponse(BaseModel):
    """Schema for flight response."""
    flight_id: str
    airline_name: str
    operator_name: Optional[str] = None
    departure_airport: str
    arrival_airport: str
    departure_datetime: datetime
    arrival_datetime: datetime
    duration_minutes: Optional[int] = None
    flight_class: str
    base_price: Decimal
    total_seats: int
    available_seats: int
    rating: float = 0.0
    total_reviews: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FlightSearchParams(BaseModel):
    """Schema for flight search parameters."""
    departure_airport: Optional[str] = Field(None, min_length=3, max_length=5)
    arrival_airport: Optional[str] = Field(None, min_length=3, max_length=5)
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    flight_class: Optional[FlightClass] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    airline_name: Optional[str] = None
    min_departure_time: Optional[str] = Field(None, description="HH:MM format")
    max_departure_time: Optional[str] = Field(None, description="HH:MM format")
    min_arrival_time: Optional[str] = Field(None, description="HH:MM format")
    max_arrival_time: Optional[str] = Field(None, description="HH:MM format")
    num_passengers: int = Field(default=1, ge=1, le=9)
    sort_by: Optional[str] = Field(default="price", description="price, duration, departure")
    sort_order: Optional[str] = Field(default="asc", description="asc or desc")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=1000)
    
    @field_validator('departure_airport', 'arrival_airport')
    @classmethod
    def uppercase_airport(cls, v):
        if v:
            return v.upper()
        return v


class FlightSearchResponse(BaseModel):
    """Schema for flight search results."""
    flights: List[FlightResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: dict = {}

