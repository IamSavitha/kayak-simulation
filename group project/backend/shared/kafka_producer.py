"""
Kafka Producer for User and Admin Events
Publishes events to Kafka topics for inter-service communication.
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
from aiokafka import AIOKafkaProducer
from kafka import KafkaProducer
from kafka.errors import KafkaError

from .config import settings

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for Kafka messages"""
    # User events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    
    # Admin events
    ADMIN_CREATED = "admin_created"
    ADMIN_UPDATED = "admin_updated"
    ADMIN_DELETED = "admin_deleted"
    ADMIN_LOGIN = "admin_login"
    
    # Listing events
    LISTING_CREATED = "listing_created"
    LISTING_UPDATED = "listing_updated"
    LISTING_DELETED = "listing_deleted"
    
    # Booking events
    BOOKING_CREATED = "booking_created"
    BOOKING_UPDATED = "booking_updated"
    BOOKING_CANCELLED = "booking_cancelled"
    
    # Billing events
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"


class KafkaEventProducer:
    """
    Synchronous Kafka producer for publishing events.
    Use this in non-async contexts.
    """
    
    _instance: Optional['KafkaEventProducer'] = None
    _producer: Optional[KafkaProducer] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._producer is None:
            self._connect()
    
    def _connect(self):
        """Connect to Kafka broker"""
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Connected to Kafka: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self._producer = None
    
    def publish(
        self,
        topic: str,
        event_type: EventType,
        data: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """
        Publish an event to a Kafka topic.
        
        Args:
            topic: Kafka topic name
            event_type: Type of event
            data: Event payload
            key: Optional message key for partitioning
            
        Returns:
            True if published successfully
        """
        if not self._producer:
            logger.warning("Kafka producer not connected, skipping publish")
            return False
        
        # Message format aligned with Team 5's producer.py
        message = {
            "event_type": event_type.value,
            "data": data,
            "_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "kayak-backend"
            }
        }
        
        try:
            future = self._producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Published event to {topic}: {event_type.value} "
                f"(partition={record_metadata.partition}, offset={record_metadata.offset})"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            return False
    
    def close(self):
        """Close the producer connection"""
        if self._producer:
            self._producer.close()
            self._producer = None
            logger.info("Kafka producer closed")


class AsyncKafkaEventProducer:
    """
    Asynchronous Kafka producer for publishing events.
    Use this in async contexts (FastAPI).
    """
    
    _instance: Optional['AsyncKafkaEventProducer'] = None
    _producer: Optional[AIOKafkaProducer] = None
    _started: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def start(self):
        """Start the async producer"""
        if not self._started:
            try:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    acks='all'
                )
                await self._producer.start()
                self._started = True
                logger.info(f"Async Kafka producer started: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            except Exception as e:
                logger.error(f"Failed to start async Kafka producer: {e}")
                self._producer = None
    
    async def publish(
        self,
        topic: str,
        event_type: EventType,
        data: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """
        Publish an event to a Kafka topic asynchronously.
        
        Args:
            topic: Kafka topic name
            event_type: Type of event
            data: Event payload
            key: Optional message key for partitioning
            
        Returns:
            True if published successfully
        """
        if not self._producer or not self._started:
            logger.warning("Async Kafka producer not started, attempting to start...")
            await self.start()
            if not self._started:
                return False
        
        # Message format aligned with Team 5's producer.py
        message = {
            "event_type": event_type.value,
            "data": data,
            "_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "source": "kayak-backend"
            }
        }
        
        try:
            await self._producer.send_and_wait(topic, value=message, key=key)
            logger.info(f"Published async event to {topic}: {event_type.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish async event to {topic}: {e}")
            return False
    
    async def stop(self):
        """Stop the async producer"""
        if self._producer and self._started:
            await self._producer.stop()
            self._started = False
            logger.info("Async Kafka producer stopped")


# Convenience functions for publishing specific events

class UserEventPublisher:
    """Publisher for user-related events"""
    
    def __init__(self, producer: Optional[KafkaEventProducer] = None):
        self.producer = producer or KafkaEventProducer()
        self.topic = settings.KAFKA_TOPIC_USER_EVENTS
    
    def publish_user_created(self, user_data: Dict[str, Any]) -> bool:
        """Publish user created event"""
        return self.producer.publish(
            topic=self.topic,
            event_type=EventType.USER_CREATED,
            data=user_data,
            key=user_data.get('user_id')
        )
    
    def publish_user_updated(self, user_id: str, updated_fields: Dict[str, Any]) -> bool:
        """Publish user updated event"""
        return self.producer.publish(
            topic=self.topic,
            event_type=EventType.USER_UPDATED,
            data={"user_id": user_id, "updated_fields": updated_fields},
            key=user_id
        )
    
    def publish_user_deleted(self, user_id: str) -> bool:
        """Publish user deleted event"""
        return self.producer.publish(
            topic=self.topic,
            event_type=EventType.USER_DELETED,
            data={"user_id": user_id},
            key=user_id
        )
    
    def publish_user_login(self, user_id: str, metadata: Optional[Dict] = None) -> bool:
        """Publish user login event"""
        return self.producer.publish(
            topic=self.topic,
            event_type=EventType.USER_LOGIN,
            data={"user_id": user_id, "metadata": metadata or {}},
            key=user_id
        )


class AsyncUserEventPublisher:
    """Async publisher for user-related events"""
    
    def __init__(self):
        self.producer = AsyncKafkaEventProducer()
        self.topic = settings.KAFKA_TOPIC_USER_EVENTS
    
    async def start(self):
        """Start the producer"""
        await self.producer.start()
    
    async def publish_user_created(self, user_data: Dict[str, Any]) -> bool:
        """Publish user created event"""
        return await self.producer.publish(
            topic=self.topic,
            event_type=EventType.USER_CREATED,
            data=user_data,
            key=user_data.get('user_id')
        )
    
    async def publish_user_updated(self, user_id: str, updated_fields: Dict[str, Any]) -> bool:
        """Publish user updated event"""
        return await self.producer.publish(
            topic=self.topic,
            event_type=EventType.USER_UPDATED,
            data={"user_id": user_id, "updated_fields": updated_fields},
            key=user_id
        )
    
    async def publish_user_deleted(self, user_id: str) -> bool:
        """Publish user deleted event"""
        return await self.producer.publish(
            topic=self.topic,
            event_type=EventType.USER_DELETED,
            data={"user_id": user_id},
            key=user_id
        )
    
    async def stop(self):
        """Stop the producer"""
        await self.producer.stop()


class AdminEventPublisher:
    """Publisher for admin-related events"""
    
    def __init__(self, producer: Optional[KafkaEventProducer] = None):
        self.producer = producer or KafkaEventProducer()
        self.topic = settings.KAFKA_TOPIC_ADMIN_EVENTS
    
    def publish_admin_created(self, admin_data: Dict[str, Any]) -> bool:
        """Publish admin created event"""
        return self.producer.publish(
            topic=self.topic,
            event_type=EventType.ADMIN_CREATED,
            data=admin_data,
            key=admin_data.get('admin_id')
        )
    
    def publish_admin_login(self, admin_id: str, metadata: Optional[Dict] = None) -> bool:
        """Publish admin login event"""
        return self.producer.publish(
            topic=self.topic,
            event_type=EventType.ADMIN_LOGIN,
            data={"admin_id": admin_id, "metadata": metadata or {}},
            key=admin_id
        )


# Global producer instances
_sync_producer: Optional[KafkaEventProducer] = None
_async_producer: Optional[AsyncKafkaEventProducer] = None


def get_kafka_producer() -> KafkaEventProducer:
    """Get the synchronous Kafka producer singleton"""
    global _sync_producer
    if _sync_producer is None:
        _sync_producer = KafkaEventProducer()
    return _sync_producer


async def get_async_kafka_producer() -> AsyncKafkaEventProducer:
    """Get the asynchronous Kafka producer singleton"""
    global _async_producer
    if _async_producer is None:
        _async_producer = AsyncKafkaEventProducer()
        await _async_producer.start()
    return _async_producer


def close_kafka_producers():
    """Close all Kafka producers"""
    global _sync_producer, _async_producer
    
    if _sync_producer:
        _sync_producer.close()
        _sync_producer = None
    
    # Note: async producer should be closed with await in an async context


