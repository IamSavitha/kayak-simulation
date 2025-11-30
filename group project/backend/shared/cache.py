"""
Redis caching utilities for Kayak Simulation.
Implements SQL caching using Redis as required by the project.
"""

import redis
import json
import hashlib
from typing import Optional, Any, Callable, TypeVar
from functools import wraps
import logging
import asyncio
from datetime import timedelta

from .config import settings

logger = logging.getLogger(__name__)


# ==================== Cache Key Generators (Team 5 Standard) ====================

class CacheKeys:
    """
    Cache key generators - aligned with Team 5's cache.py.
    All teams should use these key patterns for consistency.
    """
    
    PREFIX = "kayak"
    
    @staticmethod
    def user(user_id: str) -> str:
        """Key for user data by ID"""
        return f"{CacheKeys.PREFIX}:user:{user_id}"
    
    @staticmethod
    def user_bookings(user_id: str) -> str:
        """Key for user's booking history"""
        return f"{CacheKeys.PREFIX}:user:{user_id}:bookings"
    
    @staticmethod
    def flight(flight_id: str) -> str:
        """Key for flight data"""
        return f"{CacheKeys.PREFIX}:flight:{flight_id}"
    
    @staticmethod
    def flight_search(params_hash: str) -> str:
        """Key for flight search results"""
        return f"{CacheKeys.PREFIX}:flight_search:{params_hash}"
    
    @staticmethod
    def hotel(hotel_id: str) -> str:
        """Key for hotel data"""
        return f"{CacheKeys.PREFIX}:hotel:{hotel_id}"
    
    @staticmethod
    def hotel_search(params_hash: str) -> str:
        """Key for hotel search results"""
        return f"{CacheKeys.PREFIX}:hotel_search:{params_hash}"
    
    @staticmethod
    def car(car_id: str) -> str:
        """Key for car data"""
        return f"{CacheKeys.PREFIX}:car:{car_id}"
    
    @staticmethod
    def car_search(params_hash: str) -> str:
        """Key for car search results"""
        return f"{CacheKeys.PREFIX}:car_search:{params_hash}"
    
    @staticmethod
    def billing(billing_id: str) -> str:
        """Key for billing data"""
        return f"{CacheKeys.PREFIX}:billing:{billing_id}"
    
    @staticmethod
    def admin_analytics(report_type: str) -> str:
        """Key for admin analytics reports"""
        return f"{CacheKeys.PREFIX}:admin:analytics:{report_type}"
    
    @staticmethod
    def listing_reviews(listing_type: str, listing_id: str) -> str:
        """Key for listing reviews"""
        return f"{CacheKeys.PREFIX}:reviews:{listing_type}:{listing_id}"

T = TypeVar('T')

# Redis client instance
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get Redis client with connection pooling.
    """
    global _redis_client
    
    if _redis_client is None:
        pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            max_connections=50,
            decode_responses=True
        )
        _redis_client = redis.Redis(connection_pool=pool)
        
        # Test connection
        try:
            _redis_client.ping()
            logger.info("Redis connection established")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    return _redis_client


class CacheService:
    """
    Redis-based caching service for entity lookups.
    Implements SQL caching as required by the project specifications.
    """
    
    def __init__(self, prefix: str = "kayak"):
        self.redis = get_redis_client()
        self.prefix = prefix
        self.default_ttl = settings.REDIS_CACHE_TTL
    
    def _make_key(self, namespace: str, key: str) -> str:
        """Generate a namespaced cache key"""
        return f"{self.prefix}:{namespace}:{key}"
    
    def _hash_key(self, data: dict) -> str:
        """Generate a hash key from dictionary data"""
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            namespace: Cache namespace (e.g., "user", "listing")
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            cache_key = self._make_key(namespace, key)
            value = self.redis.get(cache_key)
            if value:
                logger.debug(f"Cache HIT: {cache_key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {cache_key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(
        self, 
        namespace: str, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (uses default if not specified)
            
        Returns:
            True if successful
        """
        try:
            cache_key = self._make_key(namespace, key)
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            self.redis.setex(cache_key, ttl, serialized)
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, namespace: str, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            
        Returns:
            True if key was deleted
        """
        try:
            cache_key = self._make_key(namespace, key)
            result = self.redis.delete(cache_key)
            logger.debug(f"Cache DELETE: {cache_key} (found: {result > 0})")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def invalidate_namespace(self, namespace: str) -> int:
        """
        Invalidate all keys in a namespace.
        
        Args:
            namespace: Cache namespace to invalidate
            
        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"{self.prefix}:{namespace}:*"
            keys = self.redis.keys(pattern)
            if keys:
                count = self.redis.delete(*keys)
                logger.info(f"Cache INVALIDATE namespace '{namespace}': {count} keys")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return 0
    
    def get_or_set(
        self,
        namespace: str,
        key: str,
        factory: Callable[[], T],
        ttl: Optional[int] = None
    ) -> T:
        """
        Get value from cache or compute and cache it.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            factory: Function to call if cache miss
            ttl: Time-to-live in seconds
            
        Returns:
            Cached or computed value
        """
        cached = self.get(namespace, key)
        if cached is not None:
            return cached
        
        value = factory()
        self.set(namespace, key, value, ttl)
        return value
    
    def cache_query(
        self,
        namespace: str,
        query_params: dict,
        factory: Callable[[], T],
        ttl: Optional[int] = None
    ) -> T:
        """
        Cache database query results based on query parameters.
        
        Args:
            namespace: Cache namespace
            query_params: Query parameters to use as cache key
            factory: Function to execute query if cache miss
            ttl: Time-to-live in seconds
            
        Returns:
            Query results (cached or fresh)
        """
        key = self._hash_key(query_params)
        return self.get_or_set(namespace, key, factory, ttl)


def cached(
    namespace: str,
    key_func: Optional[Callable[..., str]] = None,
    ttl: Optional[int] = None
):
    """
    Decorator for caching function results.
    
    Args:
        namespace: Cache namespace
        key_func: Function to generate cache key from arguments
        ttl: Time-to-live in seconds
        
    Usage:
        @cached("user", key_func=lambda user_id: user_id)
        def get_user(user_id: str):
            return db.query(User).filter(User.id == user_id).first()
    """
    cache_service = CacheService()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and arguments
                key_data = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                cache_key = cache_service._hash_key(key_data)
            
            # Try to get from cache
            cached_value = cache_service.get(namespace, cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(namespace, cache_key, result, ttl)
            return result
        
        # Add cache invalidation method
        def invalidate(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
                cache_service.delete(namespace, cache_key)
        
        wrapper.invalidate = invalidate
        wrapper.cache_service = cache_service
        return wrapper
    
    return decorator


# Singleton cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get singleton cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


class UserCache:
    """
    Specialized cache for User entities.
    Implements user lookup caching as required by the project.
    """
    
    NAMESPACE = "user"
    
    def __init__(self):
        self.cache = get_cache_service()
    
    def get_user(self, user_id: str) -> Optional[dict]:
        """Get cached user by ID"""
        return self.cache.get(self.NAMESPACE, user_id)
    
    def set_user(self, user_id: str, user_data: dict, ttl: int = 3600) -> bool:
        """Cache user data"""
        return self.cache.set(self.NAMESPACE, user_id, user_data, ttl)
    
    def invalidate_user(self, user_id: str) -> bool:
        """Invalidate user cache"""
        return self.cache.delete(self.NAMESPACE, user_id)
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get cached user by email"""
        return self.cache.get(f"{self.NAMESPACE}:email", email)
    
    def set_user_by_email(self, email: str, user_data: dict, ttl: int = 3600) -> bool:
        """Cache user data by email"""
        return self.cache.set(f"{self.NAMESPACE}:email", email, user_data, ttl)
    
    def invalidate_user_by_email(self, email: str) -> bool:
        """Invalidate user cache by email"""
        return self.cache.delete(f"{self.NAMESPACE}:email", email)


class AdminCache:
    """Specialized cache for Admin entities"""
    
    NAMESPACE = "admin"
    
    def __init__(self):
        self.cache = get_cache_service()
    
    def get_admin(self, admin_id: str) -> Optional[dict]:
        """Get cached admin by ID"""
        return self.cache.get(self.NAMESPACE, admin_id)
    
    def set_admin(self, admin_id: str, admin_data: dict, ttl: int = 3600) -> bool:
        """Cache admin data"""
        return self.cache.set(self.NAMESPACE, admin_id, admin_data, ttl)
    
    def invalidate_admin(self, admin_id: str) -> bool:
        """Invalidate admin cache"""
        return self.cache.delete(self.NAMESPACE, admin_id)


