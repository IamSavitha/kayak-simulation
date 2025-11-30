"""
Admin Service - FastAPI Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .routes import router as admin_router
from shared.config import settings
from shared.database import init_mysql_tables, close_connections
from shared.validators import ValidationError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Kayak Admin Service",
    description="Admin management service for Kayak Simulation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_router)


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    error_traceback = traceback.format_exc()
    logger.error(f"Unexpected error: {exc}")
    logger.error(f"Traceback: {error_traceback}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"}
    )


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Admin Service...")
    try:
        init_mysql_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Admin Service...")
    close_connections()


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "admin-service", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {"service": "Kayak Admin Service", "version": "1.0.0", "docs": "/docs"}


# Run with: uvicorn backend.admin_service.main:app --reload --port 8006
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)


