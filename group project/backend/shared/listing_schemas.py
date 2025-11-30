"""
Listing Schemas - Aligned with Team 2's Pydantic schemas
For use in Admin Service and AI Service

Team 2 Service Endpoints:
- Flights: http://localhost:8002
- Hotels: http://localhost:8003
- Cars: http://localhost:8004
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== Flight Schemas (from Team 2) ====================

class FlightClass(str, Enum):
    ECONOMY = "Economy"
    BUSINESS = "Business"
    FIRST = "First"


class FlightCreate(BaseModel):
    """Schema for creating a new flight - used by Admin Service"""
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

    @field_validator('arrival_date_time')
    @classmethod
    def validate_arrival_after_departure(cls, v, info):
        if 'departure_date_time' in info.data and v <= info.data['departure_date_time']:
            raise ValueError('Arrival time must be after departure time')
        return v

    model_config = {
        "json_schema_extra": {
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
    }


class FlightUpdate(BaseModel):
    """Schema for updating a flight - all fields optional"""
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
    """Response schema for flight data from Team 2's API"""
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

    model_config = {"from_attributes": True}


class FlightSearchResponse(BaseModel):
    """Paginated search response for flights"""
    flights: List[FlightResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Hotel Schemas (from Team 2) ====================

class HotelCreate(BaseModel):
    """Schema for creating a new hotel - used by Admin Service"""
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
    """Schema for updating a hotel - all fields optional"""
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
    """Response schema for hotel data from Team 2's API"""
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
    """Paginated search response for hotels"""
    hotels: List[HotelResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Car Schemas (from Team 2) ====================

class TransmissionType(str, Enum):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    RESERVED = "Reserved"


class CarCreate(BaseModel):
    """Schema for creating a new car - used by Admin Service"""
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
    """Schema for updating a car - all fields optional"""
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
    """Response schema for car data from Team 2's API"""
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
    """Paginated search response for cars"""
    cars: List[CarResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Search Query Schemas ====================

class FlightSearchQuery(BaseModel):
    """Query parameters for flight search"""
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[datetime] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    flight_class: Optional[FlightClass] = None
    departure_time_start: Optional[str] = None  # HH:MM format
    departure_time_end: Optional[str] = None
    arrival_time_start: Optional[str] = None
    arrival_time_end: Optional[str] = None
    page: int = 1
    page_size: int = 20


class HotelSearchQuery(BaseModel):
    """Query parameters for hotel search"""
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_stars: Optional[int] = None
    max_stars: Optional[int] = None
    amenities: Optional[str] = None  # Comma-separated list
    page: int = 1
    page_size: int = 20


class CarSearchQuery(BaseModel):
    """Query parameters for car search"""
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    car_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    transmission_type: Optional[TransmissionType] = None
    min_seats: Optional[int] = None
    max_seats: Optional[int] = None
    page: int = 1
    page_size: int = 20

