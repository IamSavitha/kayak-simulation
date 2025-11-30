"""
Kafka configuration and producer setup
"""
import os
import json
from typing import Dict, Any
from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_LISTING_UPDATES = os.getenv("KAFKA_TOPIC_LISTING_UPDATES", "listing_updates")

class KafkaProducer:
    """Kafka producer for listing events"""
    
    _producer: AIOKafkaProducer = None
    
    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        """Get or create Kafka producer"""
        if cls._producer is None:
            cls._producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
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
                'event_type': event_type,  # listing_created, listing_updated, listing_deleted
                'listing_type': listing_type,  # flight, hotel, car
                'listing_id': listing_id,
                'timestamp': data.get('timestamp'),
                'data': data
            }
            await producer.send_and_wait(KAFKA_TOPIC_LISTING_UPDATES, event)
        except Exception as e:
            print(f"Kafka send error: {e}")

