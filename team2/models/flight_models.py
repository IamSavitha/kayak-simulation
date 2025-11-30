"""
Flight data models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class FlightClass(str, Enum):
    ECONOMY = "Economy"
    BUSINESS = "Business"
    FIRST = "First"

class FlightCreate(BaseModel):
    airline: str = Field(..., min_length=1, max_length=100)
    departure_airport: str = Field(..., min_length=3, max_length=10)
    arrival_airport: str = Field(..., min_length=3, max_length=10)
    departure_date_time: datetime
    arrival_date_time: datetime
    duration_minutes: int = Field(..., gt=0)
    flight_class: FlightClass = FlightClass.ECONOMY
    ticket_price: float = Field(..., gt=0)
    total_available_seats: int = Field(..., ge=0)
    current_available_seats: Optional[int] = None

    @validator('arrival_date_time')
    def validate_arrival_after_departure(cls, v, values):
        if 'departure_date_time' in values and v <= values['departure_date_time']:
            raise ValueError('Arrival time must be after departure time')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "airline": "American Airlines",
                "departure_airport": "JFK",
                "arrival_airport": "LAX",
                "departure_date_time": "2024-06-01T10:00:00",
                "arrival_date_time": "2024-06-01T13:30:00",
                "duration_minutes": 330,
                "flight_class": "Economy",
                "ticket_price": 299.99,
                "total_available_seats": 150,
                "current_available_seats": 150
            }
        }

class FlightUpdate(BaseModel):
    airline: Optional[str] = None
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    departure_date_time: Optional[datetime] = None
    arrival_date_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    flight_class: Optional[FlightClass] = None
    ticket_price: Optional[float] = None
    total_available_seats: Optional[int] = None
    current_available_seats: Optional[int] = None

class FlightResponse(BaseModel):
    flight_id: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_date_time: datetime
    arrival_date_time: datetime
    duration_minutes: int
    flight_class: str
    ticket_price: float
    total_available_seats: int
    current_available_seats: int
    flight_rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FlightSearchParams(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[datetime] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    flight_class: Optional[FlightClass] = None
    departure_time_start: Optional[str] = None  # HH:MM format
    departure_time_end: Optional[str] = None    # HH:MM format
    arrival_time_start: Optional[str] = None   # HH:MM format
    arrival_time_end: Optional[str] = None     # HH:MM format
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class FlightSearchResponse(BaseModel):
    flights: list[FlightResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

