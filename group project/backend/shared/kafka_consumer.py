"""
Kafka Consumer Service for consuming messages from Kafka topics.
Aligned with Team 5's consumer.py implementation.
"""
import json
import logging
import asyncio
from typing import Optional, List, Callable, Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from aiokafka import AIOKafkaConsumer
import threading

from .config import settings

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """Synchronous Kafka Consumer wrapper - aligned with Team 5."""
    
    def __init__(
        self,
        topics: List[str],
        group_id: str = None,
        auto_offset_reset: str = 'earliest'
    ):
        """
        Initialize Kafka consumer.
        
        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
        """
        self.topics = topics
        self.group_id = group_id or settings.KAFKA_GROUP_ID
        self.auto_offset_reset = auto_offset_reset
        self._consumer: Optional[KafkaConsumer] = None
        self._running = False
        self._handlers: Dict[str, Callable] = {}
    
    def _initialize_consumer(self):
        """Initialize the Kafka consumer."""
        try:
            self._consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                max_poll_records=100,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info(f"Kafka consumer initialized for topics: {self.topics}")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            raise
    
    def register_handler(self, topic: str, handler: Callable):
        """
        Register a message handler for a specific topic.
        
        Args:
            topic: The topic name
            handler: Function to call with message value
        """
        self._handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")
    
    def start(self):
        """Start consuming messages."""
        if self._running:
            logger.warning("Consumer already running")
            return
        
        self._initialize_consumer()
        self._running = True
        
        logger.info("Starting Kafka consumer...")
        try:
            for message in self._consumer:
                if not self._running:
                    break
                
                try:
                    self._process_message(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KafkaError as e:
            logger.error(f"Kafka consumer error: {e}")
        finally:
            self.stop()
    
    def start_background(self):
        """Start consumer in a background thread."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread
    
    def _process_message(self, message):
        """Process a single message."""
        topic = message.topic
        value = message.value
        key = message.key
        
        logger.debug(
            f"Received message from {topic} - "
            f"partition: {message.partition}, "
            f"offset: {message.offset}"
        )
        
        # Call registered handler
        handler = self._handlers.get(topic)
        if handler:
            try:
                handler(value, key, message)
            except Exception as e:
                logger.error(f"Handler error for topic {topic}: {e}")
        else:
            logger.warning(f"No handler registered for topic: {topic}")
    
    def stop(self):
        """Stop consuming messages."""
        self._running = False
        if self._consumer:
            self._consumer.close()
            self._consumer = None
            logger.info("Kafka consumer stopped")


class AsyncKafkaConsumerService:
    """Asynchronous Kafka Consumer for use with FastAPI - aligned with Team 5."""
    
    def __init__(
        self,
        topics: List[str],
        group_id: str = None,
        auto_offset_reset: str = 'earliest'
    ):
        self.topics = topics
        self.group_id = group_id or settings.KAFKA_GROUP_ID
        self.auto_offset_reset = auto_offset_reset
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._running = False
        self._handlers: Dict[str, Callable] = {}
    
    async def _initialize_consumer(self):
        """Initialize the async Kafka consumer."""
        try:
            self._consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None
            )
            await self._consumer.start()
            logger.info(f"Async Kafka consumer initialized for topics: {self.topics}")
        except Exception as e:
            logger.error(f"Failed to initialize async Kafka consumer: {e}")
            raise
    
    def register_handler(self, topic: str, handler: Callable):
        """Register an async message handler."""
        self._handlers[topic] = handler
        logger.info(f"Registered async handler for topic: {topic}")
    
    async def start(self):
        """Start consuming messages asynchronously."""
        if self._running:
            return
        
        await self._initialize_consumer()
        self._running = True
        
        logger.info("Starting async Kafka consumer...")
        try:
            async for message in self._consumer:
                if not self._running:
                    break
                
                try:
                    await self._process_message(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            logger.error(f"Async Kafka consumer error: {e}")
        finally:
            await self.stop()
    
    async def _process_message(self, message):
        """Process a single message asynchronously."""
        topic = message.topic
        value = message.value
        key = message.key
        
        handler = self._handlers.get(topic)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(value, key, message)
                else:
                    handler(value, key, message)
            except Exception as e:
                logger.error(f"Handler error for topic {topic}: {e}")
    
    async def stop(self):
        """Stop the async consumer."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            logger.info("Async Kafka consumer stopped")


# ==================== Message Handlers ====================

class MessageHandlers:
    """Collection of message handler functions - aligned with Team 5."""
    
    @staticmethod
    async def handle_user_event(value: dict, key: str, message):
        """Handle user-related events."""
        event_type = value.get("event_type")
        data = value.get("data", {})
        
        logger.info(f"Processing user event: {event_type} for user {key}")
        
        if event_type == "created":
            # Handle user creation - invalidate caches, etc.
            pass
        elif event_type == "updated":
            # Handle user update - invalidate user cache
            pass
        elif event_type == "deleted":
            # Handle user deletion - cleanup
            pass
    
    @staticmethod
    async def handle_booking_event(value: dict, key: str, message):
        """Handle booking-related events."""
        event_type = value.get("event_type")
        data = value.get("data", {})
        
        logger.info(f"Processing booking event: {event_type} for booking {key}")
        
        if event_type == "created":
            # Update inventory, send confirmation
            pass
        elif event_type == "cancelled":
            # Restore inventory, process refund
            pass
    
    @staticmethod
    async def handle_payment_event(value: dict, key: str, message):
        """Handle payment-related events."""
        event_type = value.get("event_type")
        data = value.get("data", {})
        
        logger.info(f"Processing payment event: {event_type} for payment {key}")
        
        if event_type == "completed":
            # Update booking status, send receipt
            pass
        elif event_type == "failed":
            # Handle failed payment
            pass
    
    @staticmethod
    async def handle_analytics_event(value: dict, key: str, message):
        """Handle analytics events for logging to MongoDB."""
        event_type = value.get("event_type")
        data = value.get("data", {})
        
        logger.debug(f"Processing analytics event: {event_type}")
        # Store in MongoDB for analysis
    
    @staticmethod
    async def handle_deal_event(value: dict, key: str, message):
        """Handle AI deal events for the Concierge Agent."""
        event_type = value.get("event_type")
        data = value.get("data", {})
        
        logger.info(f"Processing deal event: {event_type}")
        # Forward to connected WebSocket clients

