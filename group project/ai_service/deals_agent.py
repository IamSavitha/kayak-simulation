"""
Deals Agent - Backend Worker for Deal Detection and Tagging
Ingests CSV feeds, detects deals, scores them, and publishes to Kafka.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import csv
from io import StringIO
from pathlib import Path
import random

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from pydantic import BaseModel

from .models import (
    DealBase, FlightDeal, HotelDeal, ScoredDeal, TaggedDeal,
    DealTag, ListingType, NormalizedListing, DealEvent,
    RawFlightFeed, RawHotelFeed
)
from .csv_ingestion import (
    CSVIngestionService, CSVIngestionStats,
    FlightCSVParser, AirbnbCSVParser, HotelBookingCSVParser,
    process_csv_in_batches
)

logger = logging.getLogger(__name__)


class DealsAgentConfig(BaseModel):
    """Configuration for Deals Agent (aligned with Team 5)"""
    kafka_bootstrap_servers: str = "localhost:29092"  # Team 5 uses 29092!
    consumer_group: str = "deals-agent"
    # All topics use kayak. prefix per Team 5's topics.py
    raw_feeds_topic: str = "kayak.ai.raw_supplier_feeds"
    normalized_topic: str = "kayak.ai.deals.normalized"
    scored_topic: str = "kayak.ai.deals.scored"
    tagged_topic: str = "kayak.ai.deals.tagged"
    events_topic: str = "kayak.ai.deal.events"
    
    # Deal detection thresholds
    price_drop_threshold: float = 0.15  # 15% below average
    limited_inventory_threshold: int = 5
    rolling_avg_days: int = 30


class PriceHistory:
    """In-memory price history for calculating averages"""
    
    def __init__(self, max_days: int = 30):
        self.max_days = max_days
        self._history: Dict[str, List[tuple]] = {}  # listing_id -> [(date, price), ...]
    
    def add_price(self, listing_id: str, price: float, date: datetime = None):
        """Add a price point to history"""
        date = date or datetime.utcnow()
        if listing_id not in self._history:
            self._history[listing_id] = []
        
        # Clean old entries
        cutoff = datetime.utcnow() - timedelta(days=self.max_days)
        self._history[listing_id] = [
            (d, p) for d, p in self._history[listing_id] if d > cutoff
        ]
        
        self._history[listing_id].append((date, price))
    
    def get_average(self, listing_id: str) -> Optional[float]:
        """Get rolling average price"""
        if listing_id not in self._history or not self._history[listing_id]:
            return None
        
        prices = [p for _, p in self._history[listing_id]]
        return sum(prices) / len(prices)
    
    def get_price_vs_avg(self, listing_id: str, current_price: float) -> Optional[float]:
        """Get current price relative to average (e.g., -0.15 = 15% below)"""
        avg = self.get_average(listing_id)
        if avg is None or avg == 0:
            return None
        return (current_price - avg) / avg


class DealsAgent:
    """
    Deals Agent - Detects and tags travel deals.
    
    Responsibilities:
    - Ingest CSV feeds via Kafka
    - Normalize currency/dates
    - Detect deals (≥15% price drop, limited inventory, promos)
    - Score deals (0-100)
    - Tag deals (refundable, pet-friendly, etc.)
    - Publish to Kafka topics
    """
    
    def __init__(self, config: DealsAgentConfig = None):
        self.config = config or DealsAgentConfig()
        self.price_history = PriceHistory(self.config.rolling_avg_days)
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._running = False
    
    async def start(self):
        """Start the deals agent"""
        logger.info("Starting Deals Agent...")
        
        try:
            # Initialize Kafka producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            await self.producer.start()
            
            # Initialize Kafka consumer
            self.consumer = AIOKafkaConsumer(
                self.config.raw_feeds_topic,
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                group_id=self.config.consumer_group,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            await self.consumer.start()
            
            self._running = True
            logger.info("Deals Agent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Deals Agent: {e}")
            raise
    
    async def stop(self):
        """Stop the deals agent"""
        self._running = False
        
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        
        logger.info("Deals Agent stopped")
    
    async def run(self):
        """Main processing loop"""
        await self.start()
        
        try:
            async for message in self.consumer:
                if not self._running:
                    break
                
                try:
                    await self.process_feed(message.value)
                except Exception as e:
                    logger.error(f"Error processing feed: {e}")
        finally:
            await self.stop()
    
    async def process_feed(self, feed_data: Dict[str, Any]):
        """Process a raw feed message"""
        feed_type = feed_data.get('type', 'unknown')
        records = feed_data.get('records', [])
        
        logger.info(f"Processing {len(records)} {feed_type} records")
        
        for record in records:
            try:
                # Normalize
                normalized = self.normalize_record(record, feed_type)
                if normalized:
                    await self.publish(self.config.normalized_topic, normalized.model_dump())
                    
                    # Score
                    scored = self.score_deal(normalized)
                    if scored and scored.deal_score > 0:
                        await self.publish(self.config.scored_topic, scored.model_dump())
                        
                        # Tag
                        tagged = self.tag_deal(scored)
                        await self.publish(self.config.tagged_topic, tagged.model_dump())
                        
                        # Emit event if high score
                        if tagged.deal_score >= 50:
                            event = DealEvent(
                                event_type="new_deal",
                                deal=tagged
                            )
                            await self.publish(self.config.events_topic, event.model_dump())
                            
            except Exception as e:
                logger.error(f"Error processing record: {e}")
    
    def normalize_record(self, record: Dict[str, Any], feed_type: str) -> Optional[NormalizedListing]:
        """Normalize a raw feed record"""
        try:
            if feed_type == 'flight':
                return NormalizedListing(
                    listing_id=f"FL-{record.get('origin', '')}-{record.get('destination', '')}-{datetime.now().timestamp()}",
                    listing_type=ListingType.FLIGHT,
                    name=f"{record.get('origin', '')} → {record.get('destination', '')}",
                    provider=record.get('airline', 'Unknown'),
                    price=float(record.get('price', 0)),
                    currency="USD",
                    date=datetime.strptime(record.get('departure_date', ''), '%Y-%m-%d').date() if record.get('departure_date') else datetime.now().date(),
                    location=record.get('destination'),
                    metadata={
                        'origin': record.get('origin'),
                        'destination': record.get('destination'),
                        'stops': record.get('stops', 0),
                        'duration': record.get('duration'),
                        'fare_class': record.get('fare_class')
                    }
                )
            elif feed_type == 'hotel':
                return NormalizedListing(
                    listing_id=record.get('listing_id', f"HT-{datetime.now().timestamp()}"),
                    listing_type=ListingType.HOTEL,
                    name=record.get('name', 'Unknown Hotel'),
                    provider=record.get('provider', 'Unknown'),
                    price=float(record.get('price', 0)),
                    currency="USD",
                    date=datetime.strptime(record.get('date', ''), '%Y-%m-%d').date() if record.get('date') else datetime.now().date(),
                    location=record.get('location'),
                    metadata={
                        'neighborhood': record.get('neighbourhood'),
                        'availability': record.get('availability'),
                        'amenities': record.get('amenities', '').split(',') if record.get('amenities') else [],
                        'star_rating': record.get('star_rating')
                    }
                )
        except Exception as e:
            logger.error(f"Normalization error: {e}")
        
        return None
    
    def score_deal(self, listing: NormalizedListing) -> Optional[ScoredDeal]:
        """
        Score a deal based on:
        - Price vs 30-day average
        - Inventory scarcity
        - Promo indicators
        """
        # Update price history
        self.price_history.add_price(listing.listing_id, listing.price)
        
        # Calculate price vs average
        price_vs_avg = self.price_history.get_price_vs_avg(listing.listing_id, listing.price)
        
        # Calculate score components
        price_score = 0
        inventory_score = 0
        tags = []
        
        # Price drop scoring
        if price_vs_avg is not None and price_vs_avg <= -self.config.price_drop_threshold:
            price_score = min(50, int(abs(price_vs_avg) * 100))
            tags.append(DealTag.PRICE_DROP)
        
        # Inventory scarcity scoring
        availability = listing.metadata.get('availability')
        if availability is not None and availability <= self.config.limited_inventory_threshold:
            inventory_score = 30 if availability <= 2 else 20 if availability <= 5 else 10
            tags.append(DealTag.LIMITED_AVAILABILITY)
        
        # Check for promo indicators (mock)
        if random.random() < 0.1:  # 10% chance of promo
            tags.append(DealTag.PROMO)
            price_score += 10
        
        total_score = min(100, price_score + inventory_score)
        
        if total_score == 0:
            return None
        
        deal = DealBase(
            listing_id=listing.listing_id,
            listing_type=listing.listing_type,
            name=listing.name,
            provider=listing.provider,
            price=listing.price,
            original_price=self.price_history.get_average(listing.listing_id),
            discount_percentage=abs(price_vs_avg * 100) if price_vs_avg else None
        )
        
        return ScoredDeal(
            deal=deal,
            deal_score=total_score,
            tags=tags,
            price_vs_avg=price_vs_avg
        )
    
    def tag_deal(self, scored: ScoredDeal) -> TaggedDeal:
        """
        Add tags based on listing metadata.
        Tags: Refundable/Non-refundable, Pet-friendly, Near transit, Breakfast
        """
        tags = scored.tags.copy()
        
        # This would typically come from the listing metadata
        # For now, we add some mock tags
        if scored.deal.listing_type == ListingType.HOTEL:
            # Simulate checking amenities
            if random.random() < 0.3:
                tags.append(DealTag.PET_FRIENDLY)
            if random.random() < 0.4:
                tags.append(DealTag.BREAKFAST_INCLUDED)
            if random.random() < 0.5:
                tags.append(DealTag.NEAR_TRANSIT)
            if random.random() < 0.6:
                tags.append(DealTag.REFUNDABLE)
            else:
                tags.append(DealTag.NON_REFUNDABLE)
        
        # Generate explanations
        why_this = self._generate_why_this(scored, tags)
        what_to_watch = self._generate_what_to_watch(scored, tags)
        
        return TaggedDeal(
            deal=scored.deal,
            deal_score=scored.deal_score,
            tags=list(set(tags)),  # Remove duplicates
            price_vs_avg=scored.price_vs_avg,
            why_this=why_this,
            what_to_watch=what_to_watch
        )
    
    def _generate_why_this(self, scored: ScoredDeal, tags: List[DealTag]) -> str:
        """Generate 'Why this' explanation (≤25 words)"""
        parts = []
        
        if DealTag.PRICE_DROP in tags and scored.price_vs_avg:
            parts.append(f"{abs(int(scored.price_vs_avg * 100))}% below average price")
        
        if DealTag.LIMITED_AVAILABILITY in tags:
            parts.append("limited rooms left")
        
        if DealTag.PET_FRIENDLY in tags:
            parts.append("pet-friendly")
        
        if DealTag.BREAKFAST_INCLUDED in tags:
            parts.append("includes breakfast")
        
        if not parts:
            parts.append("Good value for this date range")
        
        return ". ".join(parts[:3])[:100]
    
    def _generate_what_to_watch(self, scored: ScoredDeal, tags: List[DealTag]) -> str:
        """Generate 'What to watch' explanation (≤12 words)"""
        if DealTag.NON_REFUNDABLE in tags:
            return "Non-refundable rate"
        if DealTag.LIMITED_AVAILABILITY in tags:
            return "Only a few rooms left"
        if DealTag.PROMO in tags:
            return "Promo ends soon"
        return "Book soon for best rates"
    
    async def publish(self, topic: str, data: Dict[str, Any]):
        """Publish message to Kafka topic"""
        if self.producer:
            await self.producer.send_and_wait(topic, data)
            logger.debug(f"Published to {topic}: {data.get('listing_id', 'unknown')}")
    
    # ========================================
    # CSV Feed Ingestion Methods (Enhanced)
    # ========================================
    
    async def ingest_csv(self, csv_content: str, feed_type: str) -> CSVIngestionStats:
        """Ingest CSV content string"""
        stats = CSVIngestionStats(start_time=datetime.utcnow())
        
        try:
            listings = list(CSVIngestionService.parse_csv_content(csv_content, feed_type))
            
            for listing in listings:
                await self.process_normalized_listing(listing)
                stats.processed_rows += 1
            
            stats.total_rows = len(listings)
            stats.end_time = datetime.utcnow()
            
            logger.info(f"Ingested {stats.processed_rows} {feed_type} listings from CSV content")
            
        except Exception as e:
            logger.error(f"CSV ingestion failed: {e}")
            raise
        
        return stats
    
    async def ingest_csv_file(
        self, 
        file_path: str, 
        feed_type: Optional[str] = None,
        max_rows: Optional[int] = None,
        batch_size: int = 1000,
        sample_rate: float = 1.0
    ) -> CSVIngestionStats:
        """
        Ingest a CSV file from disk using batch processing.
        
        Args:
            file_path: Path to CSV file
            feed_type: Type of feed (auto-detected if not provided)
            max_rows: Maximum rows to process
            batch_size: Process in batches of this size
            sample_rate: Fraction of rows to process (0.0-1.0)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Auto-detect feed type
        if not feed_type:
            feed_type = CSVIngestionService.detect_feed_type(path.name)
            if not feed_type:
                raise ValueError(f"Could not detect feed type for {path.name}")
        
        logger.info(f"Starting CSV ingestion: {file_path} ({feed_type})")
        
        total_stats = CSVIngestionStats(start_time=datetime.utcnow())
        batch_count = 0
        
        for batch in process_csv_in_batches(file_path, feed_type, batch_size, max_rows):
            batch_count += 1
            
            for listing in batch:
                try:
                    await self.process_normalized_listing(listing)
                    total_stats.processed_rows += 1
                except Exception as e:
                    logger.warning(f"Failed to process listing: {e}")
                    total_stats.failed_rows += 1
            
            total_stats.total_rows += len(batch)
            
            # Log progress every 10 batches
            if batch_count % 10 == 0:
                logger.info(f"Batch {batch_count}: Processed {total_stats.processed_rows} listings")
            
            # Small delay to prevent overwhelming Kafka
            await asyncio.sleep(0.01)
        
        total_stats.end_time = datetime.utcnow()
        
        logger.info(
            f"CSV ingestion complete: {total_stats.processed_rows}/{total_stats.total_rows} "
            f"({total_stats.success_rate:.1f}%) in {total_stats.duration_seconds:.2f}s"
        )
        
        return total_stats
    
    async def process_normalized_listing(self, listing: NormalizedListing):
        """Process a single normalized listing through the deals pipeline"""
        try:
            # Publish to normalized topic
            if self.producer:
                await self.publish(self.config.normalized_topic, listing.model_dump())
            
            # Score the deal
            scored = self.score_deal(listing)
            
            if scored and scored.deal_score > 0:
                # Publish scored deal
                if self.producer:
                    await self.publish(self.config.scored_topic, scored.model_dump())
                
                # Tag the deal
                tagged = self.tag_deal(scored)
                if self.producer:
                    await self.publish(self.config.tagged_topic, tagged.model_dump())
                
                # Emit event for high-score deals
                if tagged.deal_score >= 50:
                    event = DealEvent(
                        event_type="new_deal",
                        deal=tagged
                    )
                    if self.producer:
                        await self.publish(self.config.events_topic, event.model_dump())
                
                # Cache the deal for the concierge
                await self.cache_deal(tagged)
                
        except Exception as e:
            logger.error(f"Error processing listing {listing.listing_id}: {e}")
    
    async def cache_deal(self, deal: TaggedDeal):
        """Cache deal for quick access by concierge"""
        if not hasattr(self, '_deal_cache'):
            self._deal_cache: Dict[str, TaggedDeal] = {}
        
        self._deal_cache[deal.deal.listing_id] = deal
        
        # Limit cache size
        if len(self._deal_cache) > 10000:
            # Remove oldest entries
            oldest_keys = list(self._deal_cache.keys())[:1000]
            for key in oldest_keys:
                del self._deal_cache[key]
    
    def get_cached_deals(self, limit: int = 100, listing_type: Optional[ListingType] = None) -> List[TaggedDeal]:
        """Get cached deals for recommendations"""
        if not hasattr(self, '_deal_cache'):
            return []
        
        deals = list(self._deal_cache.values())
        
        if listing_type:
            deals = [d for d in deals if d.deal.listing_type == listing_type]
        
        # Sort by score descending
        deals.sort(key=lambda x: x.deal_score, reverse=True)
        
        return deals[:limit]
    
    async def ingest_all_feeds(self, feeds_dir: str = "data/feeds", max_per_file: int = 10000) -> Dict[str, CSVIngestionStats]:
        """Ingest all CSV feeds from a directory"""
        feeds_path = Path(feeds_dir)
        if not feeds_path.exists():
            logger.warning(f"Feeds directory not found: {feeds_dir}")
            return {}
        
        results = {}
        
        for csv_file in feeds_path.glob("*.csv"):
            try:
                logger.info(f"Processing feed: {csv_file.name}")
                stats = await self.ingest_csv_file(
                    str(csv_file),
                    max_rows=max_per_file,
                    batch_size=500
                )
                results[csv_file.name] = stats
            except Exception as e:
                logger.error(f"Failed to process {csv_file.name}: {e}")
        
        return results


# Singleton instance
_deals_agent: Optional[DealsAgent] = None


def get_deals_agent() -> DealsAgent:
    """Get singleton Deals Agent instance"""
    global _deals_agent
    if _deals_agent is None:
        _deals_agent = DealsAgent()
    return _deals_agent


