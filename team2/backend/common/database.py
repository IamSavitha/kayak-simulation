"""
Database connections - Team 5 compatible
"""
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from pymongo.database import Database
from dbutils.pooled_db import PooledDB
import pymysql
from typing import Generator

from backend.common.config import settings

# SQLAlchemy Engine with Connection Pooling
engine = create_engine(
    settings.MYSQL_URL,
    poolclass=pool.QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PyMySQL Connection Pool for raw queries
mysql_pool = PooledDB(
    creator=pymysql,
    maxconnections=20,
    mincached=5,
    maxcached=10,
    maxshared=10,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=1,
    host=settings.MYSQL_HOST,
    port=settings.MYSQL_PORT,
    user=settings.MYSQL_USER,
    password=settings.MYSQL_PASSWORD,
    database=settings.MYSQL_DATABASE,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# MongoDB Client
mongo_client = MongoClient(
    host=settings.MONGODB_HOST,
    port=settings.MONGODB_PORT,
    serverSelectionTimeoutMS=5000
)
mongo_db: Database = mongo_client[settings.MONGODB_DATABASE]

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mysql_connection():
    """Get MySQL connection from pool"""
    return mysql_pool.connection()

def get_mongo_db() -> Database:
    """Get MongoDB database instance"""
    return mongo_db

