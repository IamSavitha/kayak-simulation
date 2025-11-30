"""
External Service Interfaces for Team 1
These interfaces define what we expect from other teams.
Aligned with Team 2's actual API documentation.

Team 2 Service Endpoints (Liza):
- Flights: http://localhost:8002
- Hotels: http://localhost:8003
- Cars: http://localhost:8004
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel
from enum import Enum


# ========================================
# Data Models - Aligned with Team 2's Schemas
# ========================================

class ListingType(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    CAR = "car"


class FlightListing(BaseModel):
    """Flight schema from Team 2's flight_schemas.py"""
    flight_id: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_date_time: datetime
    arrival_date_time: datetime
    duration_minutes: int
    flight_class: str  # Economy, Business, First
    ticket_price: float
    total_available_seats: int
    current_available_seats: int
    flight_rating: float = 0.0
    total_reviews: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HotelListing(BaseModel):
    """Hotel schema from Team 2's hotel_schemas.py"""
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
    amenities: Optional[str] = None  # Comma-separated string
    hotel_rating: float = 0.0
    total_reviews: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CarListing(BaseModel):
    """Car schema from Team 2's car_schemas.py"""
    car_id: str
    car_type: str  # SUV, Sedan, Compact, etc.
    company_provider_name: str
    model_and_year: str
    transmission_type: str  # Automatic, Manual
    number_of_seats: int
    daily_rental_price: float
    car_rating: float = 0.0
    total_reviews: int = 0
    availability_status: str = "Available"  # Available, Unavailable, Reserved
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# From Team 3 - Booking Service
class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class Booking(BaseModel):
    """Expected Booking schema from Team 3 (Barathi)"""
    booking_id: str
    user_id: str
    booking_type: ListingType
    listing_id: str
    listing_name: Optional[str] = None
    provider: Optional[str] = None
    booking_date: datetime
    check_in_date: date
    check_out_date: Optional[date] = None
    status: BookingStatus
    total_amount: float
    guests: int = 1


class Review(BaseModel):
    """Expected Review schema from Team 3 (Barathi)"""
    review_id: str
    booking_id: str
    user_id: str
    listing_id: str
    listing_type: ListingType
    rating: float
    review_text: str
    review_date: datetime
    images: Optional[List[str]] = None


# From Team 4 - Billing Service
class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    PAYPAL = "PAYPAL"
    DEBIT_CARD = "DEBIT_CARD"


class BillingRecord(BaseModel):
    """Expected Billing schema from Team 4 (Daniel)"""
    billing_id: str
    user_id: str
    booking_type: ListingType
    booking_id: str
    date_of_transaction: datetime
    total_amount_paid: float
    payment_method: PaymentMethod
    transaction_status: TransactionStatus
    invoice_reference: Optional[str] = None


class RevenueByProperty(BaseModel):
    """Revenue data for admin reports from Team 4"""
    listing_id: str
    listing_name: str
    listing_type: ListingType
    total_revenue: float
    booking_count: int


class RevenueByCity(BaseModel):
    """City revenue data for admin reports from Team 4"""
    city: str
    state: str
    total_revenue: float
    booking_count: int


# ========================================
# Service Interfaces (Abstract)
# ========================================

class ListingServiceInterface(ABC):
    """
    Interface for Team 2's Listing Service.
    TEAM 2 (Liza): Please implement these methods.
    """
    
    @abstractmethod
    async def search_flights(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        departure_date: Optional[date] = None,
        flight_class: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search flights with filters"""
        pass
    
    @abstractmethod
    async def search_hotels(
        self,
        location: Optional[str] = None,
        check_in_date: Optional[date] = None,
        check_out_date: Optional[date] = None,
        star_rating: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        amenities: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search hotels with filters"""
        pass
    
    @abstractmethod
    async def search_cars(
        self,
        location: Optional[str] = None,
        pickup_date: Optional[date] = None,
        return_date: Optional[date] = None,
        car_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search cars with filters"""
        pass
    
    @abstractmethod
    async def get_all_listings_for_ai(
        self,
        listing_type: Optional[ListingType] = None,
        limit: int = 10000
    ) -> List[Dict[str, Any]]:
        """Get all listings for AI service deal detection"""
        pass


class BookingServiceInterface(ABC):
    """
    Interface for Team 3's Booking Service.
    TEAM 3 (Barathi): Please implement these methods.
    """
    
    @abstractmethod
    async def get_user_bookings(
        self,
        user_id: str,
        status: Optional[str] = None,  # past, current, future
        booking_type: Optional[ListingType] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get bookings for a user"""
        pass
    
    @abstractmethod
    async def get_user_reviews(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get reviews submitted by a user"""
        pass


class BillingServiceInterface(ABC):
    """
    Interface for Team 4's Billing Service.
    TEAM 4 (Daniel): Please implement these methods.
    """
    
    @abstractmethod
    async def get_billing_by_date(
        self,
        date: date,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get billing records by date"""
        pass
    
    @abstractmethod
    async def get_billing_by_month(
        self,
        year: int,
        month: int,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get billing records by month"""
        pass
    
    @abstractmethod
    async def get_revenue_by_property(
        self,
        year: int,
        limit: int = 10
    ) -> List[RevenueByProperty]:
        """Get revenue grouped by property (for top 10 chart)"""
        pass
    
    @abstractmethod
    async def get_revenue_by_city(
        self,
        year: int
    ) -> List[RevenueByCity]:
        """Get revenue grouped by city (for city chart)"""
        pass


# ========================================
# Mock Implementations (For Development)
# ========================================

class MockListingService(ListingServiceInterface):
    """Mock implementation for development before Team 2 integration"""
    
    async def search_flights(self, **kwargs) -> Dict[str, Any]:
        return {
            "flights": [
                {
                    "flight_id": "FL001",
                    "airline": "United Airlines",
                    "departure_airport": "SFO",
                    "arrival_airport": "JFK",
                    "departure_datetime": "2025-02-15T08:00:00",
                    "arrival_datetime": "2025-02-15T16:30:00",
                    "duration": "5h 30m",
                    "flight_class": "ECONOMY",
                    "ticket_price": 299.00,
                    "available_seats": 15,
                    "flight_rating": 4.2
                }
            ],
            "total": 1,
            "page": 1,
            "total_pages": 1
        }
    
    async def search_hotels(self, **kwargs) -> Dict[str, Any]:
        return {
            "hotels": [
                {
                    "hotel_id": "HT001",
                    "hotel_name": "Marriott Times Square",
                    "address": "1535 Broadway",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10036",
                    "star_rating": 4,
                    "num_rooms": 5,
                    "room_type": "Double",
                    "price_per_night": 189.00,
                    "amenities": ["WiFi", "Gym", "Breakfast"],
                    "hotel_rating": 4.5
                }
            ],
            "total": 1,
            "page": 1,
            "total_pages": 1
        }
    
    async def search_cars(self, **kwargs) -> Dict[str, Any]:
        return {
            "cars": [
                {
                    "car_id": "CR001",
                    "car_type": "SUV",
                    "company_name": "Enterprise",
                    "model": "Ford Explorer",
                    "year": 2024,
                    "transmission_type": "AUTOMATIC",
                    "num_seats": 7,
                    "daily_rental_price": 89.00,
                    "car_rating": 4.3,
                    "availability_status": True
                }
            ],
            "total": 1,
            "page": 1,
            "total_pages": 1
        }
    
    async def get_all_listings_for_ai(self, **kwargs) -> List[Dict[str, Any]]:
        return [
            {"listing_id": "FL001", "listing_type": "FLIGHT", "price": 299.00},
            {"listing_id": "HT001", "listing_type": "HOTEL", "price": 189.00},
        ]


class MockBookingService(BookingServiceInterface):
    """Mock implementation for development before Team 3 integration"""
    
    async def get_user_bookings(self, user_id: str, **kwargs) -> Dict[str, Any]:
        return {
            "bookings": [
                {
                    "booking_id": "BK001",
                    "user_id": user_id,
                    "booking_type": "FLIGHT",
                    "listing_id": "FL001",
                    "listing_name": "SFO → JFK",
                    "provider": "United Airlines",
                    "booking_date": "2025-01-15T10:30:00Z",
                    "check_in_date": "2025-02-15",
                    "status": "CONFIRMED",
                    "total_amount": 299.00,
                    "guests": 1
                }
            ],
            "total": 1,
            "page": 1
        }
    
    async def get_user_reviews(self, user_id: str, **kwargs) -> Dict[str, Any]:
        return {
            "reviews": [
                {
                    "review_id": "RV001",
                    "booking_id": "BK001",
                    "listing_id": "FL001",
                    "listing_type": "FLIGHT",
                    "rating": 4.5,
                    "review_text": "Great flight!",
                    "review_date": "2025-02-20T14:00:00Z"
                }
            ],
            "total": 1
        }


class MockBillingService(BillingServiceInterface):
    """Mock implementation for development before Team 4 integration"""
    
    async def get_billing_by_date(self, date: date, **kwargs) -> Dict[str, Any]:
        return {
            "billing_records": [
                {
                    "billing_id": "BIL001",
                    "user_id": "123-45-6789",
                    "booking_type": "FLIGHT",
                    "booking_id": "BK001",
                    "date_of_transaction": "2025-01-15T10:30:00Z",
                    "total_amount_paid": 299.00,
                    "payment_method": "CREDIT_CARD",
                    "transaction_status": "COMPLETED"
                }
            ],
            "total": 1,
            "total_revenue": 299.00
        }
    
    async def get_billing_by_month(self, year: int, month: int, **kwargs) -> Dict[str, Any]:
        return await self.get_billing_by_date(date(year, month, 1), **kwargs)
    
    async def get_revenue_by_property(self, year: int, limit: int = 10) -> List[RevenueByProperty]:
        return [
            RevenueByProperty(
                listing_id=f"HT00{i}",
                listing_name=f"Hotel {i}",
                listing_type=ListingType.HOTEL,
                total_revenue=10000 - (i * 500),
                booking_count=100 - (i * 5)
            )
            for i in range(1, limit + 1)
        ]
    
    async def get_revenue_by_city(self, year: int) -> List[RevenueByCity]:
        cities = [
            ("New York", "NY", 50000),
            ("Los Angeles", "CA", 45000),
            ("San Francisco", "CA", 40000),
            ("Miami", "FL", 35000),
            ("Las Vegas", "NV", 30000),
        ]
        return [
            RevenueByCity(city=c, state=s, total_revenue=r, booking_count=int(r/100))
            for c, s, r in cities
        ]


# ========================================
# Service Factory
# ========================================

# Switch between mock and real implementations
USE_MOCK_SERVICES = True  # Set to False when real services are available


def get_listing_service() -> ListingServiceInterface:
    """Get listing service instance"""
    if USE_MOCK_SERVICES:
        return MockListingService()
    else:
        # TODO: Replace with real Team 2 service client
        # from .team2_client import ListingServiceClient
        # return ListingServiceClient(base_url="http://localhost:8003")
        return MockListingService()


def get_booking_service() -> BookingServiceInterface:
    """Get booking service instance"""
    if USE_MOCK_SERVICES:
        return MockBookingService()
    else:
        # TODO: Replace with real Team 3 service client
        return MockBookingService()


def get_billing_service() -> BillingServiceInterface:
    """Get billing service instance"""
    if USE_MOCK_SERVICES:
        return MockBillingService()
    else:
        # TODO: Replace with real Team 4 service client
        return MockBillingService()

