"""
Search Service - FastAPI application for unified search across flights, hotels, and cars.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import date
import logging

from .service import UnifiedSearchService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kayak Search Service",
    description="Unified search microservice for Kayak simulation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("Starting Search Service...")
    logger.info("Search Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Search Service...")


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    return await get_comprehensive_health(
        check_redis=True,
        service_name="search-service"
    )


@app.get("/search")
async def unified_search(
    query: Optional[str] = Query(None, description="General search query"),
    search_type: Optional[str] = Query(None, description="Filter by type: flight, hotel, car"),
    city: Optional[str] = Query(None, description="City for hotel/car search"),
    check_in: Optional[date] = Query(None, description="Check-in date"),
    check_out: Optional[date] = Query(None, description="Check-out date"),
    departure_airport: Optional[str] = Query(None, description="Departure airport code"),
    arrival_airport: Optional[str] = Query(None, description="Arrival airport code"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=1000)
):
    """Unified search across flights, hotels, and cars."""
    service = UnifiedSearchService()
    return await service.unified_search(
        query=query,
        search_type=search_type,
        city=city,
        check_in=check_in,
        check_out=check_out,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)

