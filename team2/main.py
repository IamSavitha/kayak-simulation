"""
Team 2 - Listing Services Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import flight_routes, hotel_routes, car_routes
from config.kafka_config import KafkaProducer
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Kayak Listing Services API",
    description="Team 2 - Flight, Hotel, and Car Listing Services",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flight_routes.router)
app.include_router(hotel_routes.router)
app.include_router(car_routes.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Team 2 - Listing Services",
        "version": "1.0.0",
        "endpoints": {
            "flights": "/flights",
            "hotels": "/hotels",
            "cars": "/cars",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "listing-services"}

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer on startup"""
    try:
        await KafkaProducer.get_producer()
        print("Kafka producer initialized")
    except Exception as e:
        print(f"Warning: Kafka producer initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close Kafka producer on shutdown"""
    await KafkaProducer.close()

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)

