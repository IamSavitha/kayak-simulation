"""
AI Recommendation Service - FastAPI Application
Multi-agent travel concierge with WebSocket support.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from pathlib import Path
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
import json

from .models import (
    BundleRequest, BundleResponse, ChatRequest, ChatResponse,
    PolicyQuestion, PolicyAnswer, WatchCreateRequest, Watch,
    WatchAlert, TaggedDeal, DealEvent, TripBundle
)
from .deals_agent import DealsAgent, get_deals_agent
from .concierge_agent import ConciergeAgent, get_concierge_agent
from .csv_ingestion import CSVIngestionService, CSVIngestionStats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected: {user_id}")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected: {user_id}")
    
    async def send_personal(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting AI Service...")
    
    # Initialize agents
    deals_agent = get_deals_agent()
    concierge_agent = get_concierge_agent()
    
    # Start background deal processing (if Kafka is available)
    # asyncio.create_task(deals_agent.run())
    
    yield
    
    logger.info("Shutting down AI Service...")


# Create FastAPI application
app = FastAPI(
    title="Kayak AI Recommendation Service",
    description="Multi-agent travel concierge for deals and trip recommendations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Health Check
# ========================================

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "ai-service", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Kayak AI Recommendation Service",
        "version": "1.0.0",
        "agents": ["deals_agent", "concierge_agent"],
        "docs": "/docs"
    }


# ========================================
# Bundles Endpoint
# ========================================

@app.post("/bundles", response_model=BundleResponse, tags=["Bundles"])
async def get_bundles(
    request: BundleRequest,
    concierge: ConciergeAgent = Depends(get_concierge_agent)
):
    """
    Get flight+hotel bundle recommendations based on preferences.
    
    - Composes bundles from cached deals
    - Computes Fit Score for each bundle
    - Returns top 3 recommendations
    """
    bundles = concierge.compose_bundles(request)
    
    clarifying_question = None
    if not bundles:
        clarifying_question = "No exact matches found. Would you like to expand your search dates or budget?"
    
    return BundleResponse(
        bundles=bundles,
        query_understood=f"Looking for trips to {request.destination or 'anywhere'} with budget ${request.budget or 'flexible'}",
        clarifying_question=clarifying_question
    )


# ========================================
# Chat/Concierge Endpoint
# ========================================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    concierge: ConciergeAgent = Depends(get_concierge_agent)
):
    """
    Chat with the AI concierge.
    
    - Understands natural language intent
    - Remembers conversation context
    - Returns recommendations and answers questions
    """
    return concierge.chat(request)


# ========================================
# Policy/FAQ Endpoint
# ========================================

@app.post("/policy", response_model=PolicyAnswer, tags=["Policy"])
async def answer_policy(
    question: PolicyQuestion,
    concierge: ConciergeAgent = Depends(get_concierge_agent)
):
    """
    Answer policy and FAQ questions.
    
    - Answers questions about refunds, pets, parking, etc.
    - Quotes from listing metadata when available
    """
    return concierge.answer_policy(question)


# ========================================
# Deals Endpoint
# ========================================

@app.get("/deals", tags=["Deals"])
async def get_deals(
    listing_type: Optional[str] = None,
    location: Optional[str] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
    concierge: ConciergeAgent = Depends(get_concierge_agent)
):
    """
    Get current deals.
    
    - Returns cached deals with scores and tags
    - Supports filtering by type, location, and price
    """
    if listing_type == 'flight':
        deals = concierge.deal_cache.get_flights(destination=location, max_price=max_price)
    elif listing_type == 'hotel':
        deals = concierge.deal_cache.get_hotels(location=location, max_price=max_price)
    else:
        deals = (
            concierge.deal_cache.get_flights(destination=location, max_price=max_price) +
            concierge.deal_cache.get_hotels(location=location, max_price=max_price)
        )
    
    return {
        "deals": [d.model_dump() for d in deals[:limit]],
        "total": len(deals)
    }


# ========================================
# Watch Endpoints
# ========================================

@app.post("/watches", response_model=Watch, tags=["Watches"])
async def create_watch(
    request: WatchCreateRequest,
    user_id: str = "default_user",  # Would come from auth
    concierge: ConciergeAgent = Depends(get_concierge_agent)
):
    """
    Create a price/inventory watch.
    
    - Set thresholds for price drops or low inventory
    - Get notified via WebSocket when triggered
    """
    return concierge.create_watch(user_id, request)


@app.get("/watches", tags=["Watches"])
async def list_watches(
    user_id: str = "default_user",
    concierge: ConciergeAgent = Depends(get_concierge_agent)
):
    """List all watches for a user."""
    user_watches = [w for w in concierge.watches.values() if w.user_id == user_id]
    return {"watches": [w.model_dump() for w in user_watches]}


@app.delete("/watches/{watch_id}", tags=["Watches"])
async def delete_watch(
    watch_id: str,
    concierge: ConciergeAgent = Depends(get_concierge_agent)
):
    """Delete a watch."""
    if watch_id in concierge.watches:
        del concierge.watches[watch_id]
        return {"message": f"Watch {watch_id} deleted"}
    raise HTTPException(status_code=404, detail="Watch not found")


# ========================================
# WebSocket Endpoint for Real-time Updates
# ========================================

@app.websocket("/events")
async def websocket_events(websocket: WebSocket, user_id: str = "anonymous"):
    """
    WebSocket endpoint for real-time deal and watch updates.
    
    - Receives new deal events
    - Receives watch alerts
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and process messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get('type')
                
                if message_type == 'ping':
                    await websocket.send_json({'type': 'pong'})
                elif message_type == 'subscribe_deals':
                    await websocket.send_json({
                        'type': 'subscribed',
                        'message': 'Subscribed to deal updates'
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({'error': 'Invalid JSON'})
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)


# ========================================
# Feed Ingestion Endpoints
# ========================================

# Supported feed types for documentation
SUPPORTED_FEED_TYPES = {
    "flight": "Clean_Dataset.csv - Flight Price Prediction (EaseMyTrip/India)",
    "airbnb": "listings.csv - Inside Airbnb listings",
    "hotel_booking": "hotel_booking.csv - Hotel Booking Demand dataset"
}


@app.get("/feeds/types", tags=["Feeds"])
async def get_supported_feed_types():
    """List supported CSV feed types and their expected formats."""
    return {
        "feed_types": SUPPORTED_FEED_TYPES,
        "auto_detection": True,
        "note": "Feed type is auto-detected from filename if not specified"
    }


@app.post("/feeds/ingest", tags=["Feeds"])
async def ingest_feed(
    feed_type: str,
    records: List[Dict[str, Any]],
    background_tasks: BackgroundTasks,
    deals_agent: DealsAgent = Depends(get_deals_agent)
):
    """
    Manually ingest feed records for testing.
    
    - Processes records through the deals pipeline
    - Detects, scores, and tags deals
    """
    async def process():
        feed_data = {
            'type': feed_type,
            'records': records
        }
        await deals_agent.process_feed(feed_data)
    
    background_tasks.add_task(process)
    
    return {
        "message": f"Processing {len(records)} {feed_type} records",
        "status": "queued"
    }


@app.post("/feeds/upload", tags=["Feeds"])
async def upload_csv_feed(
    file: UploadFile = File(..., description="CSV file to ingest"),
    feed_type: Optional[str] = Form(None, description="Feed type (auto-detected if not provided)"),
    max_rows: Optional[int] = Form(None, description="Maximum rows to process"),
    background_tasks: BackgroundTasks = None,
    deals_agent: DealsAgent = Depends(get_deals_agent)
):
    """
    Upload and ingest a CSV file.
    
    Supported feed types:
    - **flight**: Clean_Dataset.csv format (airline, source_city, destination_city, class, price, etc.)
    - **airbnb**: Inside Airbnb listings format (id, name, neighbourhood, price, etc.)
    - **hotel_booking**: Hotel booking demand format (hotel, adr, arrival dates, meal, etc.)
    
    Feed type is auto-detected from filename if not provided.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Read file content
    content = await file.read()
    try:
        csv_content = content.decode('utf-8')
    except UnicodeDecodeError:
        csv_content = content.decode('latin-1')
    
    # Auto-detect feed type from filename
    detected_type = feed_type or CSVIngestionService.detect_feed_type(file.filename)
    if not detected_type:
        raise HTTPException(
            status_code=400, 
            detail=f"Could not detect feed type from filename '{file.filename}'. Please specify feed_type parameter."
        )
    
    # Process in background
    async def process():
        try:
            stats = await deals_agent.ingest_csv(csv_content, detected_type)
            logger.info(f"Upload complete: {stats.processed_rows} records processed")
        except Exception as e:
            logger.error(f"Upload processing failed: {e}")
    
    background_tasks.add_task(process)
    
    # Count rows for response
    row_count = csv_content.count('\n') - 1  # Approximate
    
    return {
        "message": f"Processing {file.filename}",
        "filename": file.filename,
        "detected_feed_type": detected_type,
        "approximate_rows": row_count,
        "max_rows": max_rows,
        "status": "processing"
    }


@app.post("/feeds/ingest-file", tags=["Feeds"])
async def ingest_file_from_path(
    file_path: str = Form(..., description="Path to CSV file"),
    feed_type: Optional[str] = Form(None, description="Feed type (auto-detected if not provided)"),
    max_rows: Optional[int] = Form(10000, description="Maximum rows to process"),
    sample_rate: float = Form(1.0, description="Fraction of rows to sample (0.0-1.0)"),
    background_tasks: BackgroundTasks = None,
    deals_agent: DealsAgent = Depends(get_deals_agent)
):
    """
    Ingest a CSV file from a specified path on the server.
    
    Use this for ingesting pre-downloaded Kaggle datasets.
    
    Example paths:
    - data/feeds/flights.csv
    - data/feeds/airbnb_listings.csv
    - data/feeds/hotel_bookings.csv
    """
    # Check if file exists
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    # Detect feed type
    detected_type = feed_type or CSVIngestionService.detect_feed_type(Path(file_path).name)
    if not detected_type:
        raise HTTPException(
            status_code=400,
            detail=f"Could not detect feed type. Please specify feed_type parameter."
        )
    
    # Get file size
    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    
    # Process in background for large files
    async def process():
        try:
            stats = await deals_agent.ingest_csv_file(
                file_path, 
                feed_type=detected_type,
                max_rows=max_rows,
                sample_rate=sample_rate
            )
            logger.info(f"File ingestion complete: {stats.processed_rows}/{stats.total_rows} records")
        except Exception as e:
            logger.error(f"File ingestion failed: {e}")
    
    background_tasks.add_task(process)
    
    return {
        "message": f"Started ingestion of {file_path}",
        "file_path": file_path,
        "file_size_mb": round(file_size_mb, 2),
        "detected_feed_type": detected_type,
        "max_rows": max_rows,
        "sample_rate": sample_rate,
        "status": "processing"
    }


@app.post("/feeds/ingest-all", tags=["Feeds"])
async def ingest_all_feeds(
    feeds_dir: str = Form("data/feeds", description="Directory containing CSV files"),
    max_per_file: int = Form(10000, description="Maximum rows per file"),
    background_tasks: BackgroundTasks = None,
    deals_agent: DealsAgent = Depends(get_deals_agent)
):
    """
    Ingest all CSV files from a directory.
    
    Default directory: data/feeds/
    
    Expected files:
    - flights.csv (flight price data)
    - airbnb_listings.csv (Airbnb listings)
    - hotel_bookings.csv (hotel booking data)
    """
    feeds_path = Path(feeds_dir)
    if not feeds_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {feeds_dir}")
    
    # List CSV files
    csv_files = list(feeds_path.glob("*.csv"))
    if not csv_files:
        raise HTTPException(status_code=404, detail=f"No CSV files found in {feeds_dir}")
    
    # Process in background
    async def process():
        try:
            results = await deals_agent.ingest_all_feeds(feeds_dir, max_per_file)
            total_processed = sum(s.processed_rows for s in results.values())
            logger.info(f"All feeds ingested: {total_processed} total records from {len(results)} files")
        except Exception as e:
            logger.error(f"Batch ingestion failed: {e}")
    
    background_tasks.add_task(process)
    
    return {
        "message": f"Started ingestion of {len(csv_files)} CSV files",
        "directory": feeds_dir,
        "files": [f.name for f in csv_files],
        "max_per_file": max_per_file,
        "status": "processing"
    }


@app.get("/feeds/stats", tags=["Feeds"])
async def get_ingestion_stats(
    deals_agent: DealsAgent = Depends(get_deals_agent)
):
    """
    Get statistics about ingested deals.
    """
    cached_deals = deals_agent.get_cached_deals(limit=10000)
    
    flight_deals = [d for d in cached_deals if d.deal.listing_type.value == 'flight']
    hotel_deals = [d for d in cached_deals if d.deal.listing_type.value == 'hotel']
    
    return {
        "total_cached_deals": len(cached_deals),
        "flight_deals": len(flight_deals),
        "hotel_deals": len(hotel_deals),
        "top_deals": [
            {
                "listing_id": d.deal.listing_id,
                "name": d.deal.name,
                "price": d.deal.price,
                "score": d.deal_score,
                "tags": [t.value for t in d.tags]
            }
            for d in cached_deals[:10]
        ]
    }


# ========================================
# Sample Data Endpoints (for testing)
# ========================================

@app.post("/feeds/generate-sample", tags=["Feeds"])
async def generate_sample_deals(
    count: int = Query(100, description="Number of sample deals to generate"),
    deals_agent: DealsAgent = Depends(get_deals_agent)
):
    """
    Generate sample deals for testing (no CSV required).
    
    This creates mock flight and hotel deals in memory.
    """
    import random
    from datetime import timedelta
    from .models import NormalizedListing, ListingType
    
    cities = ["New York", "Los Angeles", "Chicago", "Miami", "San Francisco", "Seattle", "Boston", "Denver"]
    airlines = ["United", "Delta", "American", "Southwest", "JetBlue", "Alaska"]
    hotel_types = ["Resort Hotel", "City Hotel", "Boutique Hotel", "Business Hotel"]
    
    generated = 0
    
    for i in range(count):
        try:
            if i % 2 == 0:
                # Generate flight
                origin = random.choice(cities)
                dest = random.choice([c for c in cities if c != origin])
                listing = NormalizedListing(
                    listing_id=f"SAMPLE-FL-{i}",
                    listing_type=ListingType.FLIGHT,
                    name=f"{origin} → {dest}",
                    provider=random.choice(airlines),
                    price=round(random.uniform(150, 600), 2),
                    currency="USD",
                    date=(datetime.now() + timedelta(days=random.randint(1, 60))).date(),
                    location=dest,
                    metadata={
                        "origin": origin,
                        "destination": dest,
                        "stops": random.randint(0, 2),
                        "duration": f"{random.randint(2, 8)}h {random.randint(0, 59)}m",
                        "fare_class": random.choice(["Economy", "Business"])
                    }
                )
            else:
                # Generate hotel
                city = random.choice(cities)
                listing = NormalizedListing(
                    listing_id=f"SAMPLE-HT-{i}",
                    listing_type=ListingType.HOTEL,
                    name=f"{random.choice(hotel_types)} {city}",
                    provider=random.choice(hotel_types),
                    price=round(random.uniform(80, 400), 2),
                    currency="USD",
                    date=(datetime.now() + timedelta(days=random.randint(1, 60))).date(),
                    location=city,
                    metadata={
                        "neighbourhood": f"Downtown {city}",
                        "availability": random.randint(1, 20),
                        "amenities": random.sample(["wifi", "breakfast_included", "pool", "gym", "pet_friendly"], k=random.randint(1, 4)),
                        "star_rating": random.randint(3, 5)
                    }
                )
            
            await deals_agent.process_normalized_listing(listing)
            generated += 1
            
        except Exception as e:
            logger.warning(f"Failed to generate sample {i}: {e}")
    
    return {
        "message": f"Generated {generated} sample deals",
        "flights": generated // 2,
        "hotels": generated - (generated // 2)
    }


# Import datetime for sample generation
from datetime import datetime


# Run with: uvicorn ai_service.main:app --reload --port 8008
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)


