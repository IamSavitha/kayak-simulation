"""
Kafka producer - Team 5 compatible
"""
import json
from typing import Dict, Any
from aiokafka import AIOKafkaProducer
from backend.common.config import settings
from backend.kafka.topics import TOPIC_LISTING_UPDATES

class KafkaProducerService:
    """Kafka producer for listing events"""
    
    _producer: AIOKafkaProducer = None
    
    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        """Get or create Kafka producer"""
        if cls._producer is None:
            cls._producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            await cls._producer.start()
        return cls._producer
    
    @classmethod
    async def close(cls):
        """Close Kafka producer"""
        if cls._producer:
            await cls._producer.stop()
            cls._producer = None
    
    @classmethod
    async def send_listing_event(
        cls,
        event_type: str,
        listing_type: str,
        listing_id: str,
        data: Dict[str, Any]
    ):
        """Send listing update event to Kafka"""
        try:
            producer = await cls.get_producer()
            event = {
                'event_type': event_type,
                'listing_type': listing_type,
                'listing_id': listing_id,
                'timestamp': data.get('timestamp'),
                'data': data
            }
            await producer.send_and_wait(TOPIC_LISTING_UPDATES, event)
            print(f"Kafka event sent: {event_type} for {listing_type}:{listing_id}")
        except Exception as e:
            print(f"Kafka send error: {e}")

