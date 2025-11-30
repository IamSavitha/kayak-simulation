"""
Concierge Agent - Chat-Facing Agent for Trip Planning
Understands user intent, composes bundles, and provides recommendations.
"""

import logging
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import uuid
import json

from .models import (
    TripBundle, BundleRequest, BundleResponse, ChatRequest, ChatResponse,
    PolicyQuestion, PolicyAnswer, Watch, WatchCreateRequest, WatchAlert,
    TaggedDeal, FlightDeal, HotelDeal, DealTag, ListingType, WatchType
)

logger = logging.getLogger(__name__)


class ConciergeSession:
    """User session for conversation context"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def add_message(self, role: str, content: str):
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.last_activity = datetime.utcnow()
    
    def update_context(self, updates: Dict[str, Any]):
        self.context.update(updates)


class DealCache:
    """In-memory cache of available deals"""
    
    def __init__(self):
        self._flights: List[TaggedDeal] = []
        self._hotels: List[TaggedDeal] = []
        self._last_refresh = datetime.utcnow()
    
    def add_deal(self, deal: TaggedDeal):
        if deal.deal.listing_type == ListingType.FLIGHT:
            self._flights.append(deal)
        else:
            self._hotels.append(deal)
    
    def get_flights(
        self,
        origin: str = None,
        destination: str = None,
        date_from: date = None,
        date_to: date = None,
        max_price: float = None
    ) -> List[TaggedDeal]:
        """Filter and return matching flight deals"""
        results = self._flights.copy()
        
        if origin:
            results = [d for d in results if origin.upper() in d.deal.name.upper()]
        if destination:
            results = [d for d in results if destination.upper() in d.deal.name.upper()]
        if max_price:
            results = [d for d in results if d.deal.price <= max_price]
        
        return sorted(results, key=lambda x: x.deal_score, reverse=True)
    
    def get_hotels(
        self,
        location: str = None,
        date_from: date = None,
        date_to: date = None,
        max_price: float = None,
        amenities: List[str] = None
    ) -> List[TaggedDeal]:
        """Filter and return matching hotel deals"""
        results = self._hotels.copy()
        
        if location:
            results = [d for d in results if location.upper() in d.deal.name.upper()]
        if max_price:
            results = [d for d in results if d.deal.price <= max_price]
        
        # Filter by amenities/tags
        if amenities:
            for amenity in amenities:
                if amenity == 'pet_friendly':
                    results = [d for d in results if DealTag.PET_FRIENDLY in d.tags]
                elif amenity == 'breakfast':
                    results = [d for d in results if DealTag.BREAKFAST_INCLUDED in d.tags]
                elif amenity == 'refundable':
                    results = [d for d in results if DealTag.REFUNDABLE in d.tags]
        
        return sorted(results, key=lambda x: x.deal_score, reverse=True)


class ConciergeAgent:
    """
    Concierge Agent - Trip planning and recommendations.
    
    Capabilities:
    - Understand intent & constraints in natural language
    - Compose flight+hotel bundles from cached deals
    - Compute Fit Score based on user preferences
    - Generate explanations and recommendations
    - Answer policy questions
    - Set price/inventory watches
    """
    
    def __init__(self):
        self.sessions: Dict[str, ConciergeSession] = {}
        self.deal_cache = DealCache()
        self.watches: Dict[str, Watch] = {}
        
        # Load some mock deals for development
        self._load_mock_deals()
    
    def _load_mock_deals(self):
        """Load mock deals for development"""
        mock_flights = [
            TaggedDeal(
                deal=FlightDeal(
                    listing_id="FL001",
                    name="SFO → JFK",
                    provider="United Airlines",
                    price=299,
                    original_price=399,
                    origin="SFO",
                    destination="JFK",
                    airline="United",
                    departure_date=date.today() + timedelta(days=30)
                ),
                deal_score=75,
                tags=[DealTag.PRICE_DROP],
                price_vs_avg=-0.25,
                why_this="25% below average, nonstop flight",
                what_to_watch="Prices may rise soon"
            ),
            TaggedDeal(
                deal=FlightDeal(
                    listing_id="FL002",
                    name="LAX → MIA",
                    provider="Delta",
                    price=249,
                    original_price=349,
                    origin="LAX",
                    destination="MIA",
                    airline="Delta",
                    departure_date=date.today() + timedelta(days=30)
                ),
                deal_score=65,
                tags=[DealTag.PRICE_DROP, DealTag.LIMITED_AVAILABILITY],
                price_vs_avg=-0.20,
                why_this="20% discount, only 3 seats left",
                what_to_watch="Book soon, limited seats"
            ),
        ]
        
        mock_hotels = [
            TaggedDeal(
                deal=HotelDeal(
                    listing_id="HT001",
                    name="Marriott Times Square",
                    provider="Marriott",
                    price=189,
                    original_price=249,
                    location="New York, NY",
                    neighborhood="Times Square",
                    check_in_date=date.today() + timedelta(days=30),
                    check_out_date=date.today() + timedelta(days=33),
                    star_rating=4,
                    amenities=["WiFi", "Gym", "Breakfast"]
                ),
                deal_score=80,
                tags=[DealTag.PRICE_DROP, DealTag.BREAKFAST_INCLUDED, DealTag.REFUNDABLE],
                price_vs_avg=-0.24,
                why_this="24% below average, free breakfast, fully refundable",
                what_to_watch="Free cancellation until 24h before"
            ),
            TaggedDeal(
                deal=HotelDeal(
                    listing_id="HT002",
                    name="Pet Paradise Hotel",
                    provider="Independent",
                    price=149,
                    original_price=179,
                    location="Miami Beach, FL",
                    neighborhood="South Beach",
                    check_in_date=date.today() + timedelta(days=30),
                    check_out_date=date.today() + timedelta(days=33),
                    star_rating=3,
                    amenities=["WiFi", "Pet-friendly", "Beach access"]
                ),
                deal_score=70,
                tags=[DealTag.PET_FRIENDLY, DealTag.NEAR_TRANSIT],
                price_vs_avg=-0.17,
                why_this="Pet-friendly, steps from the beach",
                what_to_watch="Pet deposit required"
            ),
        ]
        
        for deal in mock_flights:
            self.deal_cache.add_deal(deal)
        for deal in mock_hotels:
            self.deal_cache.add_deal(deal)
    
    def get_or_create_session(self, session_id: str = None) -> ConciergeSession:
        """Get existing session or create new one"""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        session = ConciergeSession(session_id)
        self.sessions[session.session_id] = session
        return session
    
    def parse_intent(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse user intent from natural language.
        Extract: dates, budget, constraints, destinations
        """
        intent = {
            'action': 'search',
            'origin': None,
            'destination': None,
            'dates': None,
            'budget': None,
            'travelers': 1,
            'preferences': []
        }
        
        message_lower = message.lower()
        
        # Extract budget
        budget_match = re.search(r'\$(\d+(?:,\d+)?(?:\.\d+)?)', message)
        if budget_match:
            intent['budget'] = float(budget_match.group(1).replace(',', ''))
        
        # Extract dates (simple patterns)
        date_patterns = [
            r'(\w+\s+\d{1,2}(?:-\d{1,2})?)',  # Oct 25-27
            r'(\d{1,2}/\d{1,2})',  # 10/25
        ]
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                intent['dates'] = match.group(1)
                break
        
        # Extract preferences
        if 'pet' in message_lower or 'dog' in message_lower or 'cat' in message_lower:
            intent['preferences'].append('pet_friendly')
        if 'refund' in message_lower or 'cancel' in message_lower:
            intent['preferences'].append('refundable')
        if 'breakfast' in message_lower:
            intent['preferences'].append('breakfast')
        if 'red-eye' in message_lower or 'no red' in message_lower:
            intent['preferences'].append('no_redeye')
        
        # Extract destinations (simple approach - look for city names)
        cities = ['new york', 'nyc', 'miami', 'los angeles', 'la', 'san francisco', 
                  'sfo', 'chicago', 'seattle', 'tokyo', 'paris', 'london']
        for city in cities:
            if city in message_lower:
                if not intent['destination']:
                    intent['destination'] = city.upper()
        
        # Check for origins
        origin_match = re.search(r'from\s+(\w+)', message_lower)
        if origin_match:
            intent['origin'] = origin_match.group(1).upper()
        
        # Update with context
        if context:
            for key in ['origin', 'destination', 'budget', 'dates']:
                if not intent[key] and context.get(key):
                    intent[key] = context[key]
        
        return intent
    
    def compose_bundles(self, request: BundleRequest) -> List[TripBundle]:
        """Compose flight+hotel bundles from cached deals"""
        bundles = []
        
        # Get matching flights
        flights = self.deal_cache.get_flights(
            origin=request.origin,
            destination=request.destination,
            max_price=request.budget * 0.5 if request.budget else None
        )
        
        # Get matching hotels
        hotels = self.deal_cache.get_hotels(
            location=request.destination,
            max_price=request.budget * 0.5 if request.budget else None,
            amenities=request.preferences
        )
        
        # Combine into bundles
        for i, flight in enumerate(flights[:3]):
            for j, hotel in enumerate(hotels[:3]):
                total_price = flight.deal.price + (hotel.deal.price * 3)  # Assume 3 nights
                
                # Calculate fit score
                fit_score = self._calculate_fit_score(
                    flight, hotel, request.budget, request.preferences
                )
                
                # Combine tags
                tags = list(set(flight.tags + hotel.tags))
                
                bundle = TripBundle(
                    bundle_id=f"BDL-{i}-{j}-{uuid.uuid4().hex[:8]}",
                    flight=flight.deal,
                    hotel=hotel.deal,
                    total_price=total_price,
                    original_total=flight.deal.original_price + (hotel.deal.original_price * 3) if flight.deal.original_price and hotel.deal.original_price else None,
                    savings=None,
                    fit_score=fit_score,
                    tags=tags,
                    why_this=f"{flight.why_this}. {hotel.why_this}",
                    what_to_watch=hotel.what_to_watch
                )
                
                if bundle.original_total:
                    bundle.savings = bundle.original_total - bundle.total_price
                
                bundles.append(bundle)
        
        # Sort by fit score
        bundles.sort(key=lambda x: x.fit_score, reverse=True)
        
        return bundles[:3]
    
    def _calculate_fit_score(
        self,
        flight: TaggedDeal,
        hotel: TaggedDeal,
        budget: float = None,
        preferences: List[str] = None
    ) -> int:
        """Calculate how well a bundle fits user preferences"""
        score = 50  # Base score
        
        # Price component
        total = flight.deal.price + hotel.deal.price * 3
        if budget:
            if total <= budget:
                score += 20
            elif total <= budget * 1.1:
                score += 10
        
        # Deal quality component
        score += int((flight.deal_score + hotel.deal_score) / 4)
        
        # Preference match component
        if preferences:
            matched = 0
            for pref in preferences:
                if pref == 'pet_friendly' and DealTag.PET_FRIENDLY in hotel.tags:
                    matched += 1
                elif pref == 'refundable' and DealTag.REFUNDABLE in hotel.tags:
                    matched += 1
                elif pref == 'breakfast' and DealTag.BREAKFAST_INCLUDED in hotel.tags:
                    matched += 1
            score += matched * 10
        
        return min(100, score)
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and return response"""
        session = self.get_or_create_session(request.session_id)
        session.add_message('user', request.message)
        
        # Parse intent
        intent = self.parse_intent(request.message, session.context)
        session.update_context(intent)
        
        # Generate response
        bundles = None
        clarifying_question = None
        
        # Check if we need clarification
        if not intent['destination'] and not intent['budget']:
            clarifying_question = "Where would you like to go, and what's your budget?"
            response_text = "I'd love to help you plan your trip! " + clarifying_question
        else:
            # Build bundle request
            bundle_request = BundleRequest(
                origin=intent['origin'],
                destination=intent['destination'],
                budget=intent['budget'],
                preferences=intent['preferences']
            )
            
            bundles = self.compose_bundles(bundle_request)
            
            if bundles:
                response_text = f"I found {len(bundles)} great options for you! "
                if bundles[0].savings:
                    response_text += f"The top pick saves you ${bundles[0].savings:.0f}. "
                response_text += bundles[0].why_this
            else:
                response_text = "I couldn't find any matching deals right now. Try adjusting your dates or budget?"
        
        session.add_message('assistant', response_text)
        
        return ChatResponse(
            message=response_text,
            bundles=bundles,
            clarifying_question=clarifying_question,
            session_id=session.session_id
        )
    
    def answer_policy(self, question: PolicyQuestion) -> PolicyAnswer:
        """Answer a policy/FAQ question"""
        q_lower = question.question.lower()
        
        # Simple keyword matching for demo
        if 'refund' in q_lower or 'cancel' in q_lower:
            answer = "Most refundable rates can be cancelled up to 24 hours before check-in for a full refund. Non-refundable rates offer better prices but cannot be cancelled."
        elif 'pet' in q_lower:
            answer = "Pet policies vary by property. Look for the 'Pet-friendly' tag. Most charge a $25-75 pet deposit. Service animals are always welcome."
        elif 'parking' in q_lower:
            answer = "Parking availability and pricing varies. City hotels typically charge $20-50/night for valet. Airport hotels often include free parking."
        elif 'breakfast' in q_lower:
            answer = "Properties with 'Breakfast included' tag offer complimentary morning meals. This typically includes continental or hot breakfast buffet."
        else:
            answer = "I'm not sure about that specific policy. Please contact the property directly or check the booking details for specific terms."
        
        return PolicyAnswer(
            question=question.question,
            answer=answer,
            source="Property metadata and booking terms"
        )
    
    def create_watch(self, user_id: str, request: WatchCreateRequest) -> Watch:
        """Create a price/inventory watch"""
        watch = Watch(
            watch_id=str(uuid.uuid4()),
            user_id=user_id,
            watch_type=request.watch_type,
            listing_id=request.listing_id,
            listing_type=request.listing_type,
            price_threshold=request.price_threshold,
            inventory_threshold=request.inventory_threshold,
            origin=request.origin,
            destination=request.destination,
            date_range_start=request.date_range_start,
            date_range_end=request.date_range_end,
            max_price=request.max_price
        )
        
        self.watches[watch.watch_id] = watch
        logger.info(f"Created watch {watch.watch_id} for user {user_id}")
        
        return watch
    
    def check_watches(self, deal: TaggedDeal) -> List[WatchAlert]:
        """Check if a deal triggers any watches"""
        alerts = []
        
        for watch in self.watches.values():
            if not watch.is_active:
                continue
            
            triggered = False
            message = ""
            
            # Check price threshold
            if watch.price_threshold and deal.deal.price <= watch.price_threshold:
                triggered = True
                message = f"Price dropped to ${deal.deal.price}!"
            
            # Check inventory threshold
            if watch.inventory_threshold and DealTag.LIMITED_AVAILABILITY in deal.tags:
                triggered = True
                message = "Low inventory alert!"
            
            if triggered:
                alert = WatchAlert(
                    alert_id=str(uuid.uuid4()),
                    watch_id=watch.watch_id,
                    user_id=watch.user_id,
                    alert_type=watch.watch_type,
                    message=message,
                    deal=deal
                )
                alerts.append(alert)
                watch.last_notified = datetime.utcnow()
        
        return alerts


# Singleton instance
_concierge_agent: Optional[ConciergeAgent] = None


def get_concierge_agent() -> ConciergeAgent:
    """Get singleton Concierge Agent instance"""
    global _concierge_agent
    if _concierge_agent is None:
        _concierge_agent = ConciergeAgent()
    return _concierge_agent


