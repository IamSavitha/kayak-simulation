"""
SQLAlchemy models for MySQL database.
These models represent the core entities stored in the relational database.
"""
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, Enum, 
    ForeignKey, Boolean, Index, UniqueConstraint, DECIMAL
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..common.database import Base


# ==================== Enums ====================

class BookingType(str, enum.Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    CAR = "car"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class FlightClass(str, enum.Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"


class RoomType(str, enum.Enum):
    SINGLE = "single"
    DOUBLE = "double"
    SUITE = "suite"
    DELUXE = "deluxe"


class CarType(str, enum.Enum):
    SEDAN = "sedan"
    SUV = "suv"
    COMPACT = "compact"
    LUXURY = "luxury"
    VAN = "van"


class TransmissionType(str, enum.Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"


# ==================== User Model ====================

class User(Base):
    """User entity model."""
    __tablename__ = "users"
    
    # Primary Key - SSN format (XXX-XX-XXXX)
    user_id = Column(String(11), primary_key=True, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    
    # Address
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(2))  # State abbreviation
    zip_code = Column(String(10))
    
    # Profile
    profile_image_url = Column(String(500))
    
    # Payment Details (stored securely - in production, use encryption)
    credit_card_last_four = Column(String(4))
    credit_card_type = Column(String(20))
    
    # Password (hashed)
    password_hash = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user", lazy="dynamic")
    billings = relationship("Billing", back_populates="user", lazy="dynamic")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_name', 'first_name', 'last_name'),
    )


# ==================== Flight Model ====================

class Flight(Base):
    """Flight entity model."""
    __tablename__ = "flights"
    
    flight_id = Column(String(10), primary_key=True, index=True)  # e.g., AA123
    
    # Airline Information
    airline_name = Column(String(100), nullable=False)
    operator_name = Column(String(100))
    
    # Route Information
    departure_airport = Column(String(5), nullable=False, index=True)  # IATA code
    arrival_airport = Column(String(5), nullable=False, index=True)
    
    # Schedule
    departure_datetime = Column(DateTime, nullable=False, index=True)
    arrival_datetime = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    
    # Class and Pricing
    # Use String instead of Enum to avoid case-sensitivity issues with MySQL enum
    flight_class = Column(String(20), default=FlightClass.ECONOMY.value)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Availability
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    
    # Rating
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_flight_route', 'departure_airport', 'arrival_airport'),
        Index('idx_flight_date', 'departure_datetime'),
    )


# ==================== Hotel Model ====================

class Hotel(Base):
    """Hotel entity model."""
    __tablename__ = "hotels"
    
    hotel_id = Column(String(50), primary_key=True, index=True)
    
    # Hotel Information
    hotel_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Address
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), index=True)
    zip_code = Column(String(10))
    
    # Rating
    star_rating = Column(Integer)  # 1-5 stars
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Amenities (stored as comma-separated or JSON in real implementation)
    amenities = Column(Text)  # e.g., "wifi,breakfast,parking,pool"
    
    # Contact
    phone_number = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    
    # Image
    image_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    rooms = relationship("HotelRoom", back_populates="hotel", lazy="dynamic")
    
    __table_args__ = (
        Index('idx_hotel_location', 'city', 'state'),
    )


class HotelRoom(Base):
    """Hotel Room entity model."""
    __tablename__ = "hotel_rooms"
    
    room_id = Column(String(50), primary_key=True, index=True)
    hotel_id = Column(String(50), ForeignKey("hotels.hotel_id"), nullable=False)
    
    # Room Information
    # Use String instead of Enum to avoid case-sensitivity issues with MySQL enum
    room_type = Column(String(20), nullable=False)
    room_number = Column(String(10))
    
    # Pricing
    price_per_night = Column(DECIMAL(10, 2), nullable=False)
    
    # Capacity
    max_occupancy = Column(Integer, default=2)
    
    # Availability
    total_rooms = Column(Integer, default=1)
    available_rooms = Column(Integer, default=1)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    hotel = relationship("Hotel", back_populates="rooms")
    
    __table_args__ = (
        Index('idx_room_hotel', 'hotel_id'),
    )


# ==================== Car Model ====================

class Car(Base):
    """Car rental entity model."""
    __tablename__ = "cars"
    
    car_id = Column(String(50), primary_key=True, index=True)
    
    # Car Information
    # Use String instead of Enum to avoid case-sensitivity issues with MySQL enum
    car_type = Column(String(20), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Provider
    provider_name = Column(String(100), nullable=False, index=True)
    
    # Technical Details
    # Use String instead of Enum to avoid case-sensitivity issues with MySQL enum
    transmission_type = Column(String(20), default='AUTOMATIC')
    seats = Column(Integer, nullable=False)
    doors = Column(Integer, default=4)
    
    # Pricing
    daily_rental_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Location
    pickup_location = Column(String(255), nullable=False)
    city = Column(String(100), index=True)
    state = Column(String(2))
    
    # Rating
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Image
    image_url = Column(String(500), nullable=True)
    
    # Availability
    is_available = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_car_location', 'city', 'state'),
        Index('idx_car_provider', 'provider_name'),
    )


# ==================== Booking Model ====================

class Booking(Base):
    """Booking entity model."""
    __tablename__ = "bookings"
    
    booking_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(11), ForeignKey("users.user_id"), nullable=False)
    
    # Booking Type
    # Use String instead of Enum to avoid case-sensitivity issues with MySQL's ENUM type
    booking_type = Column(String(20), nullable=False)
    
    # Reference to the booked item
    listing_id = Column(String(50), nullable=False)  # flight_id, hotel_id, or car_id
    
    # Booking Details
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime)
    
    # For flights
    num_passengers = Column(Integer, default=1)
    
    # For hotels
    num_rooms = Column(Integer, default=1)
    num_nights = Column(Integer, default=1)
    
    # Status
    # Use String instead of Enum to avoid case-sensitivity issues with MySQL's ENUM type
    status = Column(String(20), default=BookingStatus.PENDING.value)
    
    # Pricing
    total_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Timestamps
    booking_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    billing = relationship("Billing", back_populates="booking", uselist=False)
    
    __table_args__ = (
        Index('idx_booking_user', 'user_id'),
        Index('idx_booking_type', 'booking_type'),
        Index('idx_booking_date', 'booking_date'),
        Index('idx_booking_status', 'status'),
    )


# ==================== Billing Model ====================

class Billing(Base):
    """Billing entity model."""
    __tablename__ = "billings"
    
    billing_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(11), ForeignKey("users.user_id"), nullable=False)
    booking_id = Column(String(50), ForeignKey("bookings.booking_id"), nullable=False)
    
    # Transaction Details
    booking_type = Column(String(20), nullable=False)  # Changed from Enum to String to match Booking model
    transaction_date = Column(DateTime, default=func.now())
    
    # Amount
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Payment
    payment_method = Column(String(20), nullable=False)  # Changed from Enum to String to avoid case-sensitivity issues
    payment_status = Column(String(20), default=PaymentStatus.PENDING.value)  # Changed from Enum to String
    
    # Card Details (last 4 digits only)
    card_last_four = Column(String(4))
    
    # Invoice
    invoice_number = Column(String(50), unique=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="billings")
    booking = relationship("Booking", back_populates="billing")
    
    __table_args__ = (
        Index('idx_billing_user', 'user_id'),
        Index('idx_billing_date', 'transaction_date'),
        Index('idx_billing_status', 'payment_status'),
    )


# ==================== Admin Model ====================

class Admin(Base):
    """Administrator entity model."""
    __tablename__ = "admins"
    
    admin_id = Column(String(50), primary_key=True, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    
    # Address
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))
    
    # Profile
    profile_image_url = Column(String(500))
    
    # Access
    role = Column(String(20), default="admin")  # Changed from Enum to String to avoid case-sensitivity issues
    password_hash = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    __table_args__ = (
        Index('idx_admin_email', 'email'),
    )

