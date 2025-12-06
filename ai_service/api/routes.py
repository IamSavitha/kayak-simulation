"""
API routes for AI Recommendation Service.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class BundleRequest(BaseModel):
    """Request for trip bundles."""
    origin: Optional[str] = None
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    budget: Optional[float] = None
    num_travelers: int = 1
    preferences: Optional[dict] = None


class BundleResponse(BaseModel):
    """Response with trip bundles."""
    bundles: List[dict]
    total_found: int
    query_params: dict


class ChatRequest(BaseModel):
    """Chat message request."""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class DealResponse(BaseModel):
    """Deal information response."""
    listing_id: str
    listing_type: str
    current_price: float
    avg_price: float
    discount_pct: float
    deal_score: float
    tags: List[str]


@router.get("/deals", response_model=List[DealResponse])
async def get_deals(
    listing_type: Optional[str] = Query(None, description="flight, hotel, or car"),
    min_score: float = Query(default=0, ge=0, le=100),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get current deals from the deals agent cache."""
    from ..main import deals_agent
    import asyncio
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        if not deals_agent:
            logger.warning("Deals agent not initialized, returning empty list")
            return []
        
        # If cache is empty, trigger a scan
        cached_deals = deals_agent.get_cached_deals(listing_type=listing_type)
        if not cached_deals:
            # Trigger a background scan
            try:
                asyncio.create_task(deals_agent.scan_for_deals())
                # Wait a bit for scan to complete (or return empty if scan takes too long)
                await asyncio.sleep(2)
                cached_deals = deals_agent.get_cached_deals(listing_type=listing_type)
            except Exception as scan_error:
                logger.error(f"Error during deal scan: {scan_error}")
                # Continue with empty cache if scan fails
        
        # Filter by minimum score
        filtered_deals = [
            d for d in cached_deals 
            if d.get("deal_score", 0) >= min_score
        ]
        
        # Format response
        formatted_deals = []
        for deal in filtered_deals[:limit]:
            try:
                current_price = float(deal.get("current_price", 0))
                avg_price = float(deal.get("avg_30d_price", current_price))
                discount_pct = 0.0
                if avg_price > 0 and current_price > 0:
                    discount_pct = ((avg_price - current_price) / avg_price) * 100
                
                formatted_deals.append({
                    "listing_id": str(deal.get("listing_id", "")),
                    "listing_type": str(deal.get("listing_type", "")),
                    "current_price": round(current_price, 2),
                    "avg_price": round(avg_price, 2),
                    "discount_pct": round(discount_pct, 1),
                    "deal_score": round(float(deal.get("deal_score", 0.0)), 1),
                    "tags": deal.get("tags", []) if isinstance(deal.get("tags"), list) else []
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Error formatting deal {deal.get('listing_id', 'unknown')}: {e}")
                continue
        
        return formatted_deals
    except Exception as e:
        logger.error(f"Error getting deals: {e}", exc_info=True)
        # Return empty list on error instead of raising exception
        return []


@router.post("/bundles", response_model=BundleResponse)
async def find_bundles(request: BundleRequest):
    """Find flight + hotel + car bundles."""
    from datetime import datetime, timedelta
    from decimal import Decimal
    import uuid
    
    # Import database models and session
    try:
        from backend.common.database import get_mysql_context
        from backend.models.mysql_models import Flight, Hotel, HotelRoom, Car
    except ImportError:
        # Fallback for local development
        import sys
        import os
        backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
        if os.path.exists(backend_path):
            sys.path.insert(0, os.path.abspath(backend_path))
        from backend.common.database import get_mysql_context
        from backend.models.mysql_models import Flight, Hotel, HotelRoom, Car
    
    bundles = []
    
    try:
        # Parse dates
        departure_date = datetime.strptime(request.departure_date, "%Y-%m-%d") if request.departure_date else datetime.now() + timedelta(days=30)
        return_date = datetime.strptime(request.return_date, "%Y-%m-%d") if request.return_date else departure_date + timedelta(days=7)
        num_nights = (return_date - departure_date).days
        
        if num_nights <= 0:
            num_nights = 1
        
        # City to airport code mapping
        city_to_airport = {
            "san francisco": "SFO",
            "los angeles": "LAX",
            "new york": "JFK",
            "miami": "MIA",
            "chicago": "ORD",
            "boston": "BOS",
            "seattle": "SEA",
            "denver": "DEN",
            "atlanta": "ATL",
            "phoenix": "PHX",
            "las vegas": "LAS",
            "dallas": "DFW"
        }
        
        # Normalize destination
        dest_city = request.destination.strip()
        dest_lower = dest_city.lower()
        
        # Get airport code from city name or use as-is if it's already an airport code
        if dest_lower in city_to_airport:
            dest_airport = city_to_airport[dest_lower]
        elif len(dest_city) == 3 and dest_city.isupper():
            dest_airport = dest_city.upper()
        else:
            # Try to extract airport code (first 3 chars uppercase)
            dest_airport = dest_city[:3].upper()
        
        with get_mysql_context() as db:
            # Query flights - match by airport code or allow all if destination is flexible
            flight_query = db.query(Flight).filter(
                Flight.is_active == True,
                Flight.available_seats >= request.num_travelers
            )
            
            # Try to filter by arrival airport, but don't require exact match
            matching_flights = []
            all_flights = flight_query.limit(20).all()
            
            for flight in all_flights:
                flight_arrival = flight.arrival_airport.upper()
                # Prioritize exact airport code match
                if flight_arrival == dest_airport:
                    matching_flights.insert(0, flight)  # Add to front for priority
                elif len(matching_flights) < 10:
                    # Include other flights for variety if we don't have enough matches
                    matching_flights.append(flight)
            
            # If no exact matches found, include all flights (for flexible matching)
            if not any(f.arrival_airport.upper() == dest_airport for f in matching_flights):
                flights = all_flights[:10]
            else:
                flights = matching_flights[:10]
            
            # Query hotels - match by city name
            hotel_query = db.query(Hotel).filter(
                Hotel.is_active == True
            )
            
            # Try to match by city name
            if dest_city:
                matching_hotels = []
                all_hotels = hotel_query.limit(20).all()
                for hotel in all_hotels:
                    hotel_city = (hotel.city or "").lower()
                    if dest_lower in hotel_city or hotel_city in dest_lower or not dest_city:
                        matching_hotels.append(hotel)
                    elif len(matching_hotels) < 10:
                        matching_hotels.append(hotel)
                hotels = matching_hotels[:10]
            else:
                hotels = hotel_query.limit(10).all()
            
            # Query cars - match by city name
            car_query = db.query(Car).filter(
                Car.is_active == True,
                Car.is_available == True
            )
            
            if dest_city:
                matching_cars = []
                all_cars = car_query.limit(20).all()
                for car in all_cars:
                    car_city = (car.city or "").lower()
                    if dest_lower in car_city or car_city in dest_lower or not dest_city:
                        matching_cars.append(car)
                    elif len(matching_cars) < 10:
                        matching_cars.append(car)
                cars = matching_cars[:10]
            else:
                cars = car_query.limit(10).all()
            
            # Generate bundle combinations (Flight + Hotel + Car)
            bundle_count = 0
            max_bundles = 5
            
            for flight in flights:
                if bundle_count >= max_bundles:
                    break
                
                flight_price = float(flight.base_price) * request.num_travelers
                
                for hotel in hotels:
                    if bundle_count >= max_bundles:
                        break
                    
                    # Get minimum room price for this hotel
                    min_room = db.query(HotelRoom).filter(
                        HotelRoom.hotel_id == hotel.hotel_id,
                        HotelRoom.is_active == True
                    ).order_by(HotelRoom.price_per_night).first()
                    
                    if not min_room:
                        continue
                    
                    hotel_price = float(min_room.price_per_night) * num_nights
                    
                    for car in cars:
                        if bundle_count >= max_bundles:
                            break
                        
                        # Match car location with destination
                        car_city = (car.city or "").lower()
                        dest_lower = dest_city.lower()
                        
                        # Calculate car rental price for trip duration
                        car_price = float(car.daily_rental_price) * num_nights
                        
                        # Calculate total bundle price
                        total_price = flight_price + hotel_price + car_price
                        
                        # Check budget constraint
                        if request.budget and total_price > request.budget:
                            continue
                        
                        # Calculate fit score (0-100)
                        fit_score = _calculate_fit_score(
                            flight, hotel, car, 
                            total_price, request.budget or 1000,
                            request.num_travelers, num_nights
                        )
                        
                        bundle = {
                            "bundle_id": f"BDL-{uuid.uuid4().hex[:8].upper()}",
            "flight": {
                                "id": flight.flight_id,
                                "airline": flight.airline_name,
                                "route": f"{flight.departure_airport}-{flight.arrival_airport}",
                                "price": round(flight_price, 2),
                                "departure_datetime": flight.departure_datetime.isoformat() if flight.departure_datetime else None,
                                "duration_minutes": flight.duration_minutes or 0,
                                "available_seats": flight.available_seats
            },
            "hotel": {
                                "id": hotel.hotel_id,
                                "name": hotel.hotel_name,
                                "city": hotel.city,
                                "price_per_night": round(float(min_room.price_per_night), 2),
                                "total_price": round(hotel_price, 2),
                                "stars": hotel.star_rating or 0,
                                "amenities": hotel.amenities or ""
                            },
                            "car": {
                                "id": car.car_id,
                                "make": car.make,
                                "model": car.model,
                                "car_type": car.car_type,
                                "provider": car.provider_name,
                                "daily_price": round(float(car.daily_rental_price), 2),
                                "total_price": round(car_price, 2),
                                "seats": car.seats,
                                "location": car.pickup_location
                            },
                            "total_price": round(total_price, 2),
                            "fit_score": round(fit_score, 1),
                            "explanation": _generate_bundle_explanation(flight, hotel, car, fit_score),
                            "num_nights": num_nights,
                            "num_travelers": request.num_travelers
                        }
                        
                        bundles.append(bundle)
                        bundle_count += 1
            
            # Sort by fit score (descending)
            bundles.sort(key=lambda x: x["fit_score"], reverse=True)
            
            # Limit to top 5 bundles
            bundles = bundles[:5]
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating bundles: {e}")
        # Return empty bundles on error
    
    return BundleResponse(
        bundles=bundles,
        total_found=len(bundles),
        query_params=request.model_dump()
    )


def _calculate_fit_score(flight, hotel, car, total_price, budget, num_travelers, num_nights):
    """Calculate bundle fit score (0-100)."""
    score = 50  # Base score
    
    # Price score (0-30 points)
    if budget > 0:
        price_ratio = total_price / budget
        if price_ratio <= 0.7:
            score += 30  # Excellent value
        elif price_ratio <= 0.85:
            score += 20  # Good value
        elif price_ratio <= 1.0:
            score += 10  # Acceptable
        else:
            score -= 10  # Over budget
    
    # Flight score (0-20 points)
    if flight.available_seats >= num_travelers:
        score += 10
    if flight.rating and flight.rating >= 4.0:
        score += 10
    
    # Hotel score (0-20 points)
    if hotel.star_rating:
        score += hotel.star_rating * 2  # Up to 10 points
    if hotel.rating and hotel.rating >= 4.0:
        score += 10
    
    # Car score (0-10 points)
    if car.seats >= num_travelers:
        score += 5
    if car.rating and car.rating >= 4.0:
        score += 5
    
    # Clamp score between 0-100
    return max(0, min(100, score))


def _generate_bundle_explanation(flight, hotel, car, fit_score):
    """Generate explanation text for bundle."""
    explanations = []
    
    if fit_score >= 80:
        explanations.append("Excellent value bundle")
    elif fit_score >= 60:
        explanations.append("Great combination")
    else:
        explanations.append("Good option")
    
    if hotel.star_rating and hotel.star_rating >= 4:
        explanations.append(f"{hotel.star_rating}-star hotel")
    
    if flight.rating and flight.rating >= 4.0:
        explanations.append("highly-rated flight")
    
    if car.rating and car.rating >= 4.0:
        explanations.append("quality car rental")
    
    return ". ".join(explanations) if explanations else "Complete trip package"


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat with the concierge agent and store conversation in MongoDB."""
    import sys
    import os
    import uuid
    from datetime import datetime
    
    # Import backend modules for MongoDB access
    backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
    if os.path.exists(backend_path):
        sys.path.insert(0, os.path.abspath(backend_path))
    
    from backend.common.database import get_async_mongodb, MongoCollections
    from backend.models.mongodb_models import ChatMessage, ChatSessionDocument
    from ..agents.concierge_agent import ConciergeAgent
    
    db = get_async_mongodb()
    chat_collection = db[MongoCollections.CHAT_SESSIONS]
    
    # Get or create session
    session_id = request.session_id
    if not session_id:
        session_id = f"CHAT-{uuid.uuid4().hex[:8].upper()}"
    
    # Load existing session if available
    session_doc = await chat_collection.find_one({"session_id": session_id})
    session_context = {}
    existing_messages = []
    
    if session_doc:
        session_context = session_doc.get("context", {})
        existing_messages = session_doc.get("messages", [])
        # Update last_activity
        await chat_collection.update_one(
            {"session_id": session_id},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
    
    # Process message with concierge agent
    agent = ConciergeAgent()
    response = await agent.process_message(
        message=request.message,
        user_id=request.user_id,
        context=session_context.copy()
    )
    
    # Create user message
    user_message = ChatMessage(
        role="user",
        content=request.message,
        timestamp=datetime.utcnow()
    )
    
    # Create assistant message
    assistant_message = ChatMessage(
        role="assistant",
        content=response.get("message", ""),
        timestamp=datetime.utcnow(),
        recommendations=response.get("bundles", []),
        clarification_needed=response.get("clarification_needed", False)
    )
    
    # Update context from response
    updated_context = response.get("context", session_context)
    
    # Save or update session in MongoDB
    session_document = ChatSessionDocument(
        session_id=session_id,
        user_id=request.user_id,
        messages=existing_messages + [
            user_message.model_dump(),
            assistant_message.model_dump()
        ],
        context=updated_context,
        agent_version="concierge-v1.0",
        started_at=session_doc.get("started_at", datetime.utcnow()) if session_doc else datetime.utcnow(),
        last_activity=datetime.utcnow(),
        ended_at=None
    )
    
    await chat_collection.update_one(
        {"session_id": session_id},
        {"$set": session_document.model_dump()},
        upsert=True
    )
    
    # Return response with session_id
    return {
        **response,
        "session_id": session_id
    }


@router.get("/deals/{listing_id}/history")
async def get_price_history(listing_id: str, days: int = Query(default=30, ge=1, le=90)):
    """Get price history for a listing."""
    # Mock price history
    from datetime import timedelta
    
    history = []
    base_price = 300
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        # Simulate price fluctuation
        price = base_price + (i % 10 - 5) * 10
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": price
        })
    
    return {
        "listing_id": listing_id,
        "history": history,
        "avg_price": sum(h["price"] for h in history) / len(history),
        "min_price": min(h["price"] for h in history),
        "max_price": max(h["price"] for h in history)
    }


@router.post("/watches")
async def create_watch(
    listing_id: str,
    user_id: str,
    price_threshold: Optional[float] = None,
    inventory_threshold: Optional[int] = None
):
    """Create a price/inventory watch."""
    from ..agents.concierge_agent import ConciergeAgent
    
    agent = ConciergeAgent()
    watch_id = await agent.create_watch(
        user_id=user_id,
        listing_id=listing_id,
        price_threshold=price_threshold,
        inventory_threshold=inventory_threshold
    )
    
    return {"watch_id": watch_id, "status": "active"}


@router.delete("/watches/{watch_id}")
async def delete_watch(watch_id: str):
    """Delete a watch."""
    from ..agents.concierge_agent import ConciergeAgent
    
    agent = ConciergeAgent()
    await agent.remove_watch(watch_id)
    
    return {"watch_id": watch_id, "status": "removed"}


@router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session history from MongoDB."""
    import sys
    import os
    
    # Import backend modules for MongoDB access
    backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
    if os.path.exists(backend_path):
        sys.path.insert(0, os.path.abspath(backend_path))
    
    from backend.common.database import get_async_mongodb, MongoCollections
    
    db = get_async_mongodb()
    chat_collection = db[MongoCollections.CHAT_SESSIONS]
    
    session_doc = await chat_collection.find_one({"session_id": session_id})
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Remove MongoDB _id field for response
    session_doc.pop("_id", None)
    
    return session_doc

