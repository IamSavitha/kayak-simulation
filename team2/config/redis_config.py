"""
Redis configuration and caching utilities
"""
import redis
import json
import os
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Redis connection pool
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    max_connections=50
)

redis_client = redis.Redis(connection_pool=redis_pool)

# Cache TTL (Time To Live) in seconds
CACHE_TTL = {
    'flight': 3600,  # 1 hour
    'hotel': 3600,   # 1 hour
    'car': 3600,     # 1 hour
    'search': 1800,  # 30 minutes
}

class CacheManager:
    """Redis cache manager for listings"""
    
    @staticmethod
    def get_key(entity_type: str, entity_id: str) -> str:
        """Generate cache key"""
        return f"{entity_type}:{entity_id}"
    
    @staticmethod
    def get(entity_type: str, entity_id: str) -> Optional[dict]:
        """Get entity from cache"""
        try:
            key = CacheManager.get_key(entity_type, entity_id)
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def set(entity_type: str, entity_id: str, data: dict, ttl: Optional[int] = None) -> bool:
        """Set entity in cache"""
        try:
            key = CacheManager.get_key(entity_type, entity_id)
            ttl = ttl or CACHE_TTL.get(entity_type, 3600)
            redis_client.setex(key, ttl, json.dumps(data))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(entity_type: str, entity_id: str) -> bool:
        """Delete entity from cache"""
        try:
            key = CacheManager.get_key(entity_type, entity_id)
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def invalidate_pattern(pattern: str) -> int:
        """Invalidate cache by pattern"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return 0
    
    @staticmethod
    def get_cache_stats() -> dict:
        """Get cache statistics"""
        try:
            info = redis_client.info('stats')
            return {
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_keys': redis_client.dbsize()
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {}

