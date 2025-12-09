"""
Car Service - FastAPI application for car rental management.
"""
from fastapi import FastAPI, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import logging

from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found
from ...schemas.car_schemas import CarCreate, CarUpdate, CarResponse, CarSearchParams, CarSearchResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kayak Car Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Car Service...")
    init_mysql_db()


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    return await get_comprehensive_health(
        check_mysql=True,
        check_redis=True,
        service_name="car-service"
    )


@app.post("/cars", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(car_data: CarCreate, db: Session = Depends(get_mysql_session)):
    from .service import CarService
    return CarService(db).create_car(car_data)


# ==================== Car Search Endpoints ====================

@app.get("/cars/search", response_model=CarSearchResponse)
async def search_cars(
    city: Optional[str] = None,
    car_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    provider_name: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=1000),
    db: Session = Depends(get_mysql_session)
):
    from .service import CarService
    from decimal import Decimal
    
    params = CarSearchParams(
        city=city, car_type=car_type,
        min_price=Decimal(str(min_price)) if min_price else None,
        max_price=Decimal(str(max_price)) if max_price else None,
        provider_name=provider_name,
        page=page, page_size=page_size
    )
    return CarService(db).search_cars(params)


@app.get("/cars/{car_id}", response_model=CarResponse)
async def get_car(car_id: str, db: Session = Depends(get_mysql_session)):
    from .service import CarService
    car = CarService(db).get_car(car_id)
    if not car:
        handle_not_found("Car", car_id)
    return car


@app.put("/cars/{car_id}", response_model=CarResponse)
async def update_car(car_id: str, car_data: CarUpdate, db: Session = Depends(get_mysql_session)):
    from .service import CarService
    car = CarService(db).update_car(car_id, car_data)
    if not car:
        handle_not_found("Car", car_id)
    return car


@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: str, db: Session = Depends(get_mysql_session)):
    from .service import CarService
    if not CarService(db).delete_car(car_id):
        handle_not_found("Car", car_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

