"""
AI Service - Pydantic v2 Models for Deals and Recommendations
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ========================================
# Enums
# ========================================

class ListingType(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"


class DealTag(str, Enum):
    PRICE_DROP = "price_drop"
    LIMITED_AVAILABILITY = "limited_availability"
    PROMO = "promo"
    PET_FRIENDLY = "pet_friendly"
    NEAR_TRANSIT = "near_transit"
    BREAKFAST_INCLUDED = "breakfast_included"
    REFUNDABLE = "refundable"
    NON_REFUNDABLE = "non_refundable"


# ========================================
# Deal Models
# ========================================

class DealBase(BaseModel):
    """Base deal model"""
    listing_id: str
    listing_type: ListingType
    name: str
    provider: str
    price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None


class FlightDeal(DealBase):
    """Flight deal model"""
    listing_type: ListingType = ListingType.FLIGHT
    origin: str
    destination: str
    airline: str
    departure_date: date
    arrival_date: Optional[date] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration: Optional[str] = None
    stops: int = 0
    seats_left: Optional[int] = None


class HotelDeal(DealBase):
    """Hotel deal model"""
    listing_type: ListingType = ListingType.HOTEL
    location: str
    neighborhood: Optional[str] = None
    check_in_date: date
    check_out_date: date
    room_type: Optional[str] = None
    star_rating: Optional[int] = None
    amenities: List[str] = Field(default_factory=list)
    rooms_left: Optional[int] = None
    cancellation_policy: Optional[str] = None


class ScoredDeal(BaseModel):
    """Deal with score and tags"""
    deal: DealBase
    deal_score: int = Field(ge=0, le=100)
    tags: List[DealTag] = Field(default_factory=list)
    price_vs_avg: Optional[float] = None  # e.g., -0.15 means 15% below average
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class TaggedDeal(ScoredDeal):
    """Fully tagged and enriched deal"""
    why_this: str = Field(max_length=100, description="Why this deal is good (≤25 words)")
    what_to_watch: str = Field(max_length=50, description="What to watch out for (≤12 words)")


# ========================================
# Bundle Models
# ========================================

class TripBundle(BaseModel):
    """Flight + Hotel bundle"""
    bundle_id: str
    flight: Optional[FlightDeal] = None
    hotel: Optional[HotelDeal] = None
    total_price: float
    original_total: Optional[float] = None
    savings: Optional[float] = None
    fit_score: int = Field(ge=0, le=100)
    tags: List[DealTag] = Field(default_factory=list)
    why_this: str
    what_to_watch: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BundleRequest(BaseModel):
    """Request for trip bundle recommendations"""
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    budget: Optional[float] = None
    travelers: int = 1
    preferences: List[str] = Field(default_factory=list)  # e.g., ["pet_friendly", "refundable"]
    constraints: Optional[str] = None  # Natural language constraints


class BundleResponse(BaseModel):
    """Response with trip bundles"""
    bundles: List[TripBundle]
    query_understood: str  # Summary of what we understood
    clarifying_question: Optional[str] = None  # Max 1 clarifying question


# ========================================
# Chat/Concierge Models
# ========================================

class ChatMessage(BaseModel):
    """Chat message for concierge"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request to concierge"""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response from concierge"""
    message: str
    bundles: Optional[List[TripBundle]] = None
    clarifying_question: Optional[str] = None
    session_id: str


class PolicyQuestion(BaseModel):
    """Policy/FAQ question"""
    question: str
    listing_id: Optional[str] = None


class PolicyAnswer(BaseModel):
    """Policy/FAQ answer"""
    question: str
    answer: str
    source: Optional[str] = None  # Where the info came from


# ========================================
# Watch/Alert Models
# ========================================

class WatchType(str, Enum):
    PRICE_DROP = "price_drop"
    INVENTORY_LOW = "inventory_low"
    DEAL_MATCH = "deal_match"


class Watch(BaseModel):
    """Price/inventory watch"""
    watch_id: str
    user_id: str
    watch_type: WatchType
    listing_id: Optional[str] = None
    listing_type: Optional[ListingType] = None
    
    # Thresholds
    price_threshold: Optional[float] = None  # Alert if price drops below this
    inventory_threshold: Optional[int] = None  # Alert if inventory drops below this
    
    # Match criteria
    origin: Optional[str] = None
    destination: Optional[str] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    max_price: Optional[float] = None
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_notified: Optional[datetime] = None


class WatchAlert(BaseModel):
    """Alert triggered by a watch"""
    alert_id: str
    watch_id: str
    user_id: str
    alert_type: WatchType
    message: str
    deal: Optional[TaggedDeal] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)


class WatchCreateRequest(BaseModel):
    """Request to create a watch"""
    watch_type: WatchType
    listing_id: Optional[str] = None
    listing_type: Optional[ListingType] = None
    price_threshold: Optional[float] = None
    inventory_threshold: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    max_price: Optional[float] = None


# ========================================
# Event Models (for WebSocket/Kafka)
# ========================================

class DealEvent(BaseModel):
    """Deal event for real-time updates"""
    event_type: str  # new_deal, price_change, sold_out, etc.
    deal: TaggedDeal
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WatchEvent(BaseModel):
    """Watch event for real-time alerts"""
    event_type: str  # alert_triggered, watch_matched
    alert: WatchAlert
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ========================================
# Feed Ingestion Models
# ========================================

class RawFlightFeed(BaseModel):
    """Raw flight data from CSV feed"""
    origin: str
    destination: str
    airline: str
    departure_date: str
    price: float
    stops: Optional[int] = 0
    duration: Optional[str] = None
    fare_class: Optional[str] = None


class RawHotelFeed(BaseModel):
    """Raw hotel data from CSV feed"""
    listing_id: str
    name: str
    location: str
    neighborhood: Optional[str] = None
    price: float
    date: str
    availability: Optional[int] = None
    amenities: Optional[str] = None  # Comma-separated
    star_rating: Optional[int] = None


class NormalizedListing(BaseModel):
    """Normalized listing after ingestion"""
    listing_id: str
    listing_type: ListingType
    name: str
    provider: str
    price: float
    currency: str = "USD"
    date: date
    location: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ingested_at: datetime = Field(default_factory=datetime.utcnow)


