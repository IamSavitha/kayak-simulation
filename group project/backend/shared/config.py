"""
Configuration settings for Kayak Simulation backend services
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Kayak Simulation"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MySQL Database (aligned with Team 5)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "kayak_user"
    MYSQL_PASSWORD: str = "kayak_pass"  # Team 5's password
    MYSQL_DATABASE: str = "kayak_db"
    
    # MongoDB (Team 5 uses authentication)
    MONGODB_URI: str = "mongodb://admin:kayak_mongo_pass@localhost:27017"
    MONGODB_DATABASE: str = "kayak_db"
    
    # Redis Cache (Team 5 confirmed no password for dev)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600  # 1 hour default TTL
    CACHE_TTL: int = 3600  # Alias for Team 5 compatibility
    
    # Kafka (Team 5 uses 29092, NOT 9092 as stated in their README!)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"
    KAFKA_GROUP_ID: str = "kayak_consumer_group"
    
    # Kafka Topics (confirmed with Team 5)
    KAFKA_TOPIC_USER_EVENTS: str = "user.events"
    KAFKA_TOPIC_ADMIN_EVENTS: str = "admin.events"
    KAFKA_TOPIC_RAW_FEEDS: str = "supplier_feeds"  # Team 5's official name
    KAFKA_TOPIC_DEALS_NORMALIZED: str = "deals.normalized"
    KAFKA_TOPIC_DEALS_SCORED: str = "deals.scored"
    KAFKA_TOPIC_DEALS_TAGGED: str = "deals.tagged"
    KAFKA_TOPIC_DEAL_EVENTS: str = "deal.events"
    KAFKA_TOPIC_BOOKINGS: str = "bookings.events"  # For Team 3 integration
    KAFKA_TOPIC_BILLING: str = "billing.events"    # For Team 4 integration
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # AWS S3 (for image storage)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: str = "kayak-profile-images"
    AWS_REGION: str = "us-west-2"
    
    # Service URLs (aligned with Team 5's architecture)
    USER_SERVICE_URL: str = "http://localhost:8001"      # Team 1
    FLIGHT_SERVICE_URL: str = "http://localhost:8002"    # Team 2
    HOTEL_SERVICE_URL: str = "http://localhost:8003"     # Team 2
    CAR_SERVICE_URL: str = "http://localhost:8004"       # Team 2
    BILLING_SERVICE_URL: str = "http://localhost:8005"   # Team 4
    ADMIN_SERVICE_URL: str = "http://localhost:8006"     # Team 1 (updated)
    SEARCH_SERVICE_URL: str = "http://localhost:8007"    # Team 2
    AI_SERVICE_URL: str = "http://localhost:8008"        # Team 1 (updated)
    
    # Legacy aliases (for backward compatibility)
    LISTING_SERVICE_URL: str = "http://localhost:8003"   # Points to Hotel Service
    BOOKING_SERVICE_URL: str = "http://localhost:8005"   # Team 3 (check with Barathi)
    
    @property
    def mysql_connection_string(self) -> str:
        """Get MySQL connection string"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()


