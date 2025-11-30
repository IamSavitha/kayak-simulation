"""
Database connection utilities for Kayak Simulation
Supports MySQL (SQLAlchemy) and MongoDB connections with connection pooling.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from pymongo import MongoClient
from contextlib import contextmanager
from typing import Generator, Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for MySQL models
Base = declarative_base()

# MySQL Engine with connection pooling
_mysql_engine = None
_SessionLocal = None

# MongoDB client
_mongo_client: Optional[MongoClient] = None


def get_mysql_engine():
    """
    Get MySQL SQLAlchemy engine with connection pooling.
    Uses QueuePool for efficient connection management.
    """
    global _mysql_engine
    
    if _mysql_engine is None:
        _mysql_engine = create_engine(
            settings.mysql_connection_string,
            poolclass=QueuePool,
            pool_size=10,           # Number of connections to keep open
            max_overflow=20,        # Additional connections beyond pool_size
            pool_timeout=30,        # Seconds to wait for a connection
            pool_recycle=3600,      # Recycle connections after 1 hour
            pool_pre_ping=True,     # Test connections before use
            echo=settings.DEBUG     # Log SQL statements in debug mode
        )
        
        # Log connection pool stats
        @event.listens_for(_mysql_engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(_mysql_engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            logger.debug("Connection returned to pool")
    
    return _mysql_engine


def get_session_local():
    """Get SessionLocal class for creating database sessions"""
    global _SessionLocal
    
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_mysql_engine()
        )
    
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session.
    Automatically handles session lifecycle.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_session() as db:
            db.query(User).all()
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_mongo_client() -> MongoClient:
    """
    Get MongoDB client with connection pooling.
    """
    global _mongo_client
    
    if _mongo_client is None:
        _mongo_client = MongoClient(
            settings.MONGODB_URI,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            waitQueueTimeoutMS=5000,
            serverSelectionTimeoutMS=5000
        )
        
        # Verify connection
        try:
            _mongo_client.admin.command('ping')
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    return _mongo_client


def get_mongo_db():
    """Get MongoDB database instance"""
    client = get_mongo_client()
    return client[settings.MONGODB_DATABASE]


def init_mysql_tables():
    """Initialize all MySQL tables"""
    engine = get_mysql_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("MySQL tables initialized")


def close_connections():
    """Close all database connections"""
    global _mysql_engine, _mongo_client, _SessionLocal
    
    if _mysql_engine:
        _mysql_engine.dispose()
        _mysql_engine = None
        _SessionLocal = None
        logger.info("MySQL connections closed")
    
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        logger.info("MongoDB connections closed")


# Transaction helper
class TransactionManager:
    """
    Helper class for managing database transactions.
    Ensures atomic operations and proper rollback on failure.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self._savepoint = None
    
    def __enter__(self):
        self._savepoint = self.session.begin_nested()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Exception occurred, rollback to savepoint
            self._savepoint.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
            return False
        else:
            # Success, commit the transaction
            try:
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                logger.error(f"Commit failed, rolled back: {e}")
                raise
        return True


