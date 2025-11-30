"""
Database configuration and connection management
"""
import os
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from pymongo.database import Database
from DBUtils.PooledDB import PooledDB
import pymysql
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

# MySQL Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "kayak_listings")

# MongoDB Configuration
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "kayak_listings")

# MySQL Connection String
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

# SQLAlchemy Engine with Connection Pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# MongoDB Client
mongo_client = MongoClient(
    host=MONGODB_HOST,
    port=MONGODB_PORT,
    serverSelectionTimeoutMS=5000
)
mongo_db: Database = mongo_client[MONGODB_DATABASE]

# Dependency for getting database session
def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mysql_pool():
    """Get MySQL connection from pool"""
    return mysql_pool.connection()

def get_mongo_db() -> Database:
    """Get MongoDB database instance"""
    return mongo_db

