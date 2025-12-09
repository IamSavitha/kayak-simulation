"""
Flight Service - Business logic for flight operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import logging
import math

from ...models.mysql_models import Flight
from ...schemas.flight_schemas import (
    FlightCreate, FlightUpdate, FlightSearchParams, FlightSearchResponse, FlightResponse
)
from ...common.cache import RedisCache, CacheKeys, generate_cache_key
from ...kafka.producer import event_publisher

logger = logging.getLogger(__name__)


class FlightService:
    """Service class for flight operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = RedisCache()
    
    def create_flight(self, flight_data: FlightCreate) -> Flight:
        """Create a new flight."""
        # Calculate duration
        duration = None
        if flight_data.arrival_datetime and flight_data.departure_datetime:
            delta = flight_data.arrival_datetime - flight_data.departure_datetime
            duration = int(delta.total_seconds() / 60)
        
        flight = Flight(
            flight_id=flight_data.flight_id.upper(),
            airline_name=flight_data.airline_name,
            operator_name=flight_data.operator_name,
            departure_airport=flight_data.departure_airport.upper(),
            arrival_airport=flight_data.arrival_airport.upper(),
            departure_datetime=flight_data.departure_datetime,
            arrival_datetime=flight_data.arrival_datetime,
            duration_minutes=duration,
            flight_class=flight_data.flight_class,
            base_price=flight_data.base_price,
            total_seats=flight_data.total_seats,
            available_seats=flight_data.available_seats or flight_data.total_seats
        )
        
        self.db.add(flight)
        self.db.commit()
        self.db.refresh(flight)
        
        # Publish event
        event_publisher.publish_user_event("created", {
            "flight_id": flight.flight_id,
            "route": f"{flight.departure_airport}-{flight.arrival_airport}"
        })
        
        logger.info(f"Created flight: {flight.flight_id}")
        return flight
    
    def get_flight(self, flight_id: str) -> Optional[Flight]:
        """Get flight by ID with caching."""
        cache_key = CacheKeys.flight(flight_id)
        cached = self.cache.get(cache_key)
        if cached:
            # Return cached data but need to convert to model
            return self.db.query(Flight).filter(Flight.flight_id == flight_id).first()
        
        flight = self.db.query(Flight).filter(Flight.flight_id == flight_id.upper()).first()
        
        if flight:
            self.cache.set(cache_key, {"flight_id": flight.flight_id}, ttl=1800)
        
        return flight
    
    def update_flight(self, flight_id: str, flight_data: FlightUpdate) -> Optional[Flight]:
        """Update flight information."""
        flight = self.db.query(Flight).filter(Flight.flight_id == flight_id.upper()).first()
        if not flight:
            return None
        
        update_data = flight_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(flight, field):
                setattr(flight, field, value)
        
        # Recalculate duration if times changed
        if 'departure_datetime' in update_data or 'arrival_datetime' in update_data:
            if flight.arrival_datetime and flight.departure_datetime:
                delta = flight.arrival_datetime - flight.departure_datetime
                flight.duration_minutes = int(delta.total_seconds() / 60)
        
        # Track old price for history logging
        old_price = float(flight.base_price) if flight.base_price else None
        
        self.db.commit()
        self.db.refresh(flight)
        
        # Log price history if price changed
        if 'base_price' in update_data:
            new_price = float(flight.base_price) if flight.base_price else None
            if old_price and new_price and old_price != new_price:
                # Log price history asynchronously (non-blocking)
                import asyncio
                from ...services.analytics_service.service import AnalyticsService
                
                try:
                    analytics = AnalyticsService()
                    asyncio.create_task(analytics.log_price_history(
                        listing_id=flight_id,
                        listing_type="flight",
                        price=new_price,
                        available_inventory=flight.available_seats,
                        source="manual"
                    ))
                    logger.debug(f"Price history logged for flight {flight_id}: ${old_price} -> ${new_price}")
                except Exception as e:
                    logger.error(f"Failed to log price history: {e}")
        
        # Invalidate cache
        self.cache.delete(CacheKeys.flight(flight_id))
        # Also invalidate search cache patterns
        self.cache.delete_pattern(f"{CacheKeys.PREFIX}:flight_search:*")
        
        logger.info(f"Updated flight: {flight_id}")
        return flight
    
    def delete_flight(self, flight_id: str) -> bool:
        """Delete a flight (soft delete)."""
        flight = self.db.query(Flight).filter(Flight.flight_id == flight_id.upper()).first()
        if not flight:
            return False
        
        flight.is_active = False
        self.db.commit()
        
        # Invalidate cache
        self.cache.delete(CacheKeys.flight(flight_id))
        # Also invalidate search cache patterns
        self.cache.delete_pattern(f"{CacheKeys.PREFIX}:flight_search:*")
        
        logger.info(f"Deleted flight: {flight_id}")
        return True
    
    def search_flights(self, params: FlightSearchParams) -> FlightSearchResponse:
        """Search flights with filters and pagination."""
        # Try cache first
        cache_key = CacheKeys.flight_search(generate_cache_key(**params.model_dump()))
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for flight search")
            return FlightSearchResponse(**cached)
        
        query = self.db.query(Flight).filter(Flight.is_active == True)
        
        # Airport code to city name mapping
        AIRPORT_TO_CITY = {
            'SFO': 'San Francisco', 'JFK': 'New York', 'LGA': 'New York', 'EWR': 'New York',
            'LAX': 'Los Angeles', 'ORD': 'Chicago', 'DFW': 'Dallas', 'SEA': 'Seattle',
            'BOS': 'Boston', 'MIA': 'Miami', 'ATL': 'Atlanta', 'DEN': 'Denver',
            'LAS': 'Las Vegas', 'PHX': 'Phoenix', 'IAH': 'Houston', 'CLT': 'Charlotte',
            'MSP': 'Minneapolis', 'DTW': 'Detroit', 'PHL': 'Philadelphia', 'BWI': 'Baltimore',
            'SLC': 'Salt Lake City', 'DCA': 'Washington', 'IAD': 'Washington', 'SAN': 'San Diego',
            'PDX': 'Portland', 'STL': 'St. Louis', 'BNA': 'Nashville', 'AUS': 'Austin',
            'DEL': 'Delhi', 'BOM': 'Mumbai', 'BLR': 'Bangalore', 'CCU': 'Kolkata',
            'HYD': 'Hyderabad', 'MAA': 'Chennai'
        }
        
        # City name to airport code mapping (reverse lookup)
        CITY_TO_AIRPORT = {v: k for k, v in AIRPORT_TO_CITY.items()}
        
        # Helper function to normalize airport input (code or city name)
        def normalize_airport(airport_input: str) -> Optional[str]:
            if not airport_input:
                return None
            airport_input = airport_input.strip().upper()
            
            # If it's already a 3-letter code, return it
            if len(airport_input) == 3 and airport_input.isalpha():
                return airport_input
            
            # Try to find airport code from city name
            # Check exact match first
            if airport_input in CITY_TO_AIRPORT:
                return CITY_TO_AIRPORT[airport_input]
            
            # Check case-insensitive match
            airport_input_lower = airport_input.lower()
            for city, code in CITY_TO_AIRPORT.items():
                if city.lower() == airport_input_lower:
                    return code
            
            # Check partial match (e.g., "San Francisco" contains "francisco")
            for city, code in CITY_TO_AIRPORT.items():
                if airport_input_lower in city.lower() or city.lower() in airport_input_lower:
                    return code
            
            # If no match found, try using first 3 letters as code
            if len(airport_input) >= 3:
                return airport_input[:3]
            
            return None
        
        # Apply filters
        if params.departure_airport:
            normalized_dep = normalize_airport(params.departure_airport)
            if normalized_dep:
                query = query.filter(Flight.departure_airport == normalized_dep)
        
        if params.arrival_airport:
            normalized_arr = normalize_airport(params.arrival_airport)
            if normalized_arr:
                query = query.filter(Flight.arrival_airport == normalized_arr)
        
        if params.departure_date:
            # Allow flights within a range around the requested date (±30 days for flexibility)
            # This ensures users find flights even if exact date doesn't match
            start_of_day = datetime.combine(params.departure_date, datetime.min.time())
            end_of_day = datetime.combine(params.departure_date, datetime.max.time())
            # Add 30 days buffer to find flights near the requested date
            start_range = start_of_day - timedelta(days=30)
            end_range = end_of_day + timedelta(days=30)
            query = query.filter(
                and_(
                    Flight.departure_datetime >= start_range,
                    Flight.departure_datetime <= end_range
                )
            )
        
        if params.flight_class:
            query = query.filter(Flight.flight_class == params.flight_class)
        
        if params.min_price:
            query = query.filter(Flight.base_price >= params.min_price)
        
        if params.max_price:
            query = query.filter(Flight.base_price <= params.max_price)
        
        if params.airline_name:
            query = query.filter(Flight.airline_name.ilike(f"%{params.airline_name}%"))
        
        # Check availability
        query = query.filter(Flight.available_seats >= params.num_passengers)
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if params.sort_by == "price":
            order_col = Flight.base_price
        elif params.sort_by == "duration":
            order_col = Flight.duration_minutes
        elif params.sort_by == "departure":
            order_col = Flight.departure_datetime
        else:
            order_col = Flight.base_price
        
        if params.sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
        
        # Pagination
        offset = (params.page - 1) * params.page_size
        flights = query.offset(offset).limit(params.page_size).all()
        
        total_pages = math.ceil(total_count / params.page_size) if total_count > 0 else 1
        
        result = FlightSearchResponse(
            flights=[FlightResponse.model_validate(f) for f in flights],
            total_count=total_count,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            filters_applied=params.model_dump(exclude_none=True)
        )
        
        # Cache results
        self.cache.set(cache_key, result.model_dump(), ttl=300)  # 5 minutes
        
        # Log search for analytics
        event_publisher.publish_search_event("flight", {
            "params": params.model_dump(),
            "results_count": total_count
        })
        
        return result
    
    def get_popular_routes(self, limit: int = 10) -> List[dict]:
        """Get most popular routes."""
        routes = self.db.query(
            Flight.departure_airport,
            Flight.arrival_airport,
            func.count(Flight.flight_id).label('flight_count'),
            func.min(Flight.base_price).label('min_price')
        ).filter(
            Flight.is_active == True
        ).group_by(
            Flight.departure_airport,
            Flight.arrival_airport
        ).order_by(
            func.count(Flight.flight_id).desc()
        ).limit(limit).all()
        
        return [
            {
                "departure_airport": r.departure_airport,
                "arrival_airport": r.arrival_airport,
                "flight_count": r.flight_count,
                "min_price": float(r.min_price)
            }
            for r in routes
        ]
    
    def get_airlines(self) -> List[str]:
        """Get list of all airlines."""
        airlines = self.db.query(Flight.airline_name).distinct().all()
        return [a[0] for a in airlines]
    
    async def get_flight_reviews(self, flight_id: str) -> List[dict]:
        """Get reviews for a flight from MongoDB."""
        from ...common.database import get_async_mongodb, MongoCollections
        
        db = get_async_mongodb()
        reviews = await db[MongoCollections.REVIEWS].find(
            {"listing_id": flight_id, "listing_type": "flight"}
        ).sort("created_at", -1).to_list(50)
        
        return reviews
    
    def book_seats(self, flight_id: str, num_seats: int) -> bool:
        """Book seats on a flight (reduce availability)."""
        flight = self.db.query(Flight).filter(
            Flight.flight_id == flight_id.upper()
        ).with_for_update().first()
        
        if not flight or flight.available_seats < num_seats:
            return False
        
        flight.available_seats -= num_seats
        self.db.commit()
        
        # Invalidate cache
        self.cache.delete(CacheKeys.flight(flight_id))
        
        return True
    
    def release_seats(self, flight_id: str, num_seats: int) -> bool:
        """Release seats (for cancellations)."""
        flight = self.db.query(Flight).filter(
            Flight.flight_id == flight_id.upper()
        ).with_for_update().first()
        
        if not flight:
            return False
        
        flight.available_seats = min(
            flight.available_seats + num_seats,
            flight.total_seats
        )
        self.db.commit()
        
        self.cache.delete(CacheKeys.flight(flight_id))
        
        return True

