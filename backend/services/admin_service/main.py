"""
Admin Service - FastAPI application for admin management and analytics.
"""
from fastapi import FastAPI, Depends, Query, status, HTTPException, UploadFile, File, Form
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found
from .auth import get_current_admin
from ...models.mysql_models import Admin
from ...schemas.admin_schemas import AdminLogin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kayak Admin Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Mount static files for image serving
import os
from pathlib import Path
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Admin Service...")
    init_mysql_db()


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    return await get_comprehensive_health(
        check_mysql=True,
        check_mongodb=True,
        check_redis=True,
        service_name="admin-service"
    )


# ==================== Analytics Endpoints ====================

@app.get("/analytics/revenue")
async def get_revenue_analytics(
    period: str = Query(default="monthly", description="daily, weekly, monthly, yearly"),
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get revenue analytics."""
    from .service import AdminService
    return AdminService(db).get_revenue_analytics(period, year, month)


@app.get("/analytics/top-properties")
async def get_top_properties(
    limit: int = Query(default=10, ge=1, le=50),
    year: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get top 10 properties by revenue."""
    from .service import AdminService
    return AdminService(db).get_top_properties(limit, year)


@app.get("/analytics/city-revenue")
async def get_city_revenue(
    year: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get city-wise revenue."""
    from .service import AdminService
    return AdminService(db).get_city_revenue(year)


@app.get("/analytics/top-providers")
async def get_top_providers(
    limit: int = Query(default=10, ge=1, le=50),
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get top hosts/providers with maximum properties sold."""
    from .service import AdminService
    return AdminService(db).get_top_providers(limit, month, year)


@app.get("/analytics/page-clicks")
async def get_page_clicks(db: Session = Depends(get_mysql_session)):
    """Get clicks per page analytics."""
    from .service import AdminService
    return await AdminService(db).get_page_clicks()


@app.get("/analytics/user-journey/{user_id}")
async def get_user_journey(user_id: str, db: Session = Depends(get_mysql_session)):
    """Get user journey trace diagram data."""
    from .service import AdminService
    return await AdminService(db).get_user_journey(user_id)


@app.get("/analytics/cohort")
async def get_cohort_analysis(
    city: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get cohort analysis for users from specific location."""
    from .service import AdminService
    return await AdminService(db).get_cohort_analysis(city, state)


# ==================== User Management ====================

@app.get("/users")
async def list_all_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """List all users (admin view)."""
    from .service import AdminService
    return AdminService(db).list_users(page, page_size, search)


@app.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    request: Request,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Activate/deactivate user account."""
    from .service import AdminService
    from .audit import log_admin_action
    from ...models.mysql_models import User
    
    # Get old user state for audit log
    user = db.query(User).filter(User.user_id == user_id).first()
    old_is_active = user.is_active if user else None
    
    service = AdminService(db)
    result = service.update_user_status(user_id, is_active)
    
    # Log admin action
    changes = [{
        "field": "is_active",
        "old_value": str(old_is_active) if old_is_active is not None else None,
        "new_value": str(is_active)
    }]
    
    await log_admin_action(
        admin_id=current_admin.admin_id,
        admin_email=current_admin.email,
        action_type="update_user_status",
        action_category="user_mgmt",
        entity_type="user",
        entity_id=user_id,
        changes=changes,
        endpoint=f"/users/{user_id}/status",
        method="PUT",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return result


# ==================== Booking Management ====================

@app.get("/bookings")
async def list_all_bookings(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    booking_type: Optional[str] = Query(None, description="Filter by booking type: flight, hotel, car"),
    status: Optional[str] = Query(None, description="Filter by status: pending, confirmed, cancelled, completed"),
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """List all bookings (admin only)."""
    from .service import AdminService
    return AdminService(db).list_bookings(page, page_size, booking_type, status)


@app.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get dashboard statistics (admin only)."""
    from .service import AdminService
    return AdminService(db).get_dashboard_stats()


@app.put("/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: str,
    status: str,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update booking status (admin only)."""
    from ...services.booking_service.service import BookingService
    from ...models.mysql_models import Booking, BookingStatus
    
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Validate status
    valid_statuses = [s.value for s in BookingStatus]
    if status.lower() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    booking.status = status.lower()
    db.commit()
    
    return {"message": "Booking status updated", "booking_id": booking_id, "status": status}


@app.post("/bookings/{booking_id}/cancel")
async def admin_cancel_booking(
    booking_id: str,
    cancel_data: dict = None,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Cancel a booking as admin (for unavoidable conditions or technical/business reasons).
    Automatically sets refund to pending if payment was completed."""
    from ...services.booking_service.service import BookingService
    from ...services.billing_service.service import BillingService
    from fastapi import Body
    
    # Handle JSON body
    if cancel_data is None:
        cancel_data = {}
    reason = cancel_data.get('reason') or "Cancelled by admin"
    refund_requested = cancel_data.get('refund_requested', False)
    
    booking_service = BookingService(db)
    try:
        # Admin cancellation sets status directly to cancelled (no approval needed)
        success = booking_service.cancel_booking(booking_id, reason, require_admin_approval=False)
        
        # For admin-cancelled bookings, automatically set refund to pending if payment was completed
        # Admin can then approve the refund separately
        refund_pending = False
        billing_service = BillingService(db)
        billing = billing_service.get_billing_by_booking_id(booking_id)
        
        if billing and billing.payment_status == "completed":
            try:
                # Set refund status to pending (admin can approve it separately)
                billing.payment_status = "refund_pending"
                db.commit()
                refund_pending = True
                
                # Publish event for admin notification
                from ...kafka.producer import event_publisher
                event_publisher.publish_payment_event("refund_pending", {
                    "billing_id": billing.billing_id,
                    "booking_id": booking_id,
                    "reason": reason or "Booking cancelled by admin - refund pending approval"
                })
            except Exception as refund_error:
                logger.error(f"Error creating pending refund for booking {booking_id}: {refund_error}")
        
        return {
            "status": "cancelled",
            "booking_id": booking_id,
            "refund_pending": refund_pending
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Listing Management ====================

@app.get("/listings")
async def list_all_listings(
    listing_type: Optional[str] = Query(None, description="flight, hotel, car"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """List all listings."""
    from .service import AdminService
    return AdminService(db).list_listings(listing_type, page, page_size)


# ==================== Hotel Management ====================

@app.get("/hotels")
async def get_all_hotels(
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all hotels (admin only)."""
    from ...models.mysql_models import Hotel
    from ...schemas.hotel_schemas import HotelResponse

    try:
        hotels = db.query(Hotel).order_by(Hotel.created_at.desc()).all()
        return {
            "hotels": [HotelResponse.model_validate(hotel) for hotel in hotels]
        }
    except Exception as e:
        logger.error(f"Error getting hotels: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get hotels: {str(e)}")


@app.post("/hotels")
async def create_hotel(
    hotel_data: str = Form(...),  # JSON string
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Create a new hotel (admin only) with optional image upload."""
    import json
    from ...services.hotel_service.service import HotelService
    from ...schemas.hotel_schemas import HotelCreate, HotelResponse
    from .image_upload import save_uploaded_image

    try:
        # Parse JSON data
        data = json.loads(hotel_data)
        
        # Handle image upload
        image_url = None
        if image and image.filename:
            image_url = await save_uploaded_image(image, "hotel", data.get("hotel_id", ""))
            data["image_url"] = image_url
        
        hotel_create = HotelCreate(**data)
        service = HotelService(db)
        hotel = service.create_hotel(hotel_create)

        return {
            "message": "Hotel created successfully",
            "hotel": HotelResponse.model_validate(hotel)
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating hotel: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create hotel: {str(e)}")


@app.put("/hotels/{hotel_id}")
async def update_hotel(
    hotel_id: str,
    hotel_data: str = Form(...),  # JSON string
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update hotel information (admin only) with optional image upload."""
    import json
    from ...services.hotel_service.service import HotelService
    from ...schemas.hotel_schemas import HotelUpdate, HotelResponse
    from .image_upload import save_uploaded_image, delete_image

    try:
        # Parse JSON data
        data = json.loads(hotel_data)
        
        # Handle image upload
        if image and image.filename:
            # Get old hotel to delete old image
            service = HotelService(db)
            old_hotel = service.get_hotel(hotel_id)
            if old_hotel and old_hotel.image_url:
                delete_image(old_hotel.image_url)
            
            # Save new image
            image_url = await save_uploaded_image(image, "hotel", hotel_id)
            data["image_url"] = image_url
        
        hotel_update = HotelUpdate(**data)
        hotel = service.update_hotel(hotel_id, hotel_update)

        if not hotel:
            handle_not_found("Hotel", hotel_id)

        return {
            "message": "Hotel updated successfully",
            "hotel": HotelResponse.model_validate(hotel)
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating hotel: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update hotel: {str(e)}")


@app.delete("/hotels/{hotel_id}")
async def delete_hotel(
    hotel_id: str,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a hotel (admin only)."""
    from ...services.hotel_service.service import HotelService

    try:
        service = HotelService(db)
        deleted = service.delete_hotel(hotel_id)

        if not deleted:
            handle_not_found("Hotel", hotel_id)

        return {
            "message": f"Hotel {hotel_id} deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting hotel: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete hotel: {str(e)}")


# ==================== Hotel Room Management ====================

@app.get("/hotels/{hotel_id}/rooms")
async def get_hotel_rooms(
    hotel_id: str,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all rooms for a hotel (admin only)."""
    from ...services.hotel_service.service import HotelService

    try:
        service = HotelService(db)
        rooms = service.get_hotel_rooms(hotel_id)
        return rooms
    except Exception as e:
        logger.error(f"Error getting hotel rooms: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get hotel rooms: {str(e)}")


@app.post("/hotels/{hotel_id}/rooms")
async def create_hotel_room(
    hotel_id: str,
    room_data: dict,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Create a new room for a hotel (admin only)."""
    from ...schemas.hotel_schemas import HotelRoomCreate, HotelRoomResponse
    from ...models.mysql_models import HotelRoom

    try:
        room_create = HotelRoomCreate(**room_data)

        # Create room
        room = HotelRoom(
            room_id=room_create.room_id,
            hotel_id=hotel_id,
            room_type=room_create.room_type,
            room_number=room_create.room_number,
            price_per_night=room_create.price_per_night,
            max_occupancy=room_create.max_occupancy,
            total_rooms=room_create.total_rooms,
            available_rooms=room_create.total_rooms
        )

        db.add(room)
        db.commit()
        db.refresh(room)

        return {
            "message": "Room created successfully",
            "room": HotelRoomResponse.model_validate(room)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating hotel room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create room: {str(e)}")


@app.put("/hotels/{hotel_id}/rooms/{room_id}")
async def update_hotel_room(
    hotel_id: str,
    room_id: str,
    room_data: dict,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update a hotel room (admin only)."""
    from ...schemas.hotel_schemas import HotelRoomUpdateData, HotelRoomResponse
    from ...models.mysql_models import HotelRoom

    try:
        room_update = HotelRoomUpdateData(**room_data)

        # Get room
        room = db.query(HotelRoom).filter(
            HotelRoom.room_id == room_id,
            HotelRoom.hotel_id == hotel_id
        ).first()

        if not room:
            handle_not_found("Room", room_id)

        # Update fields
        for key, value in room_update.model_dump(exclude_unset=True).items():
            setattr(room, key, value)

        db.commit()
        db.refresh(room)

        return {
            "message": "Room updated successfully",
            "room": HotelRoomResponse.model_validate(room)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating hotel room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update room: {str(e)}")


@app.delete("/hotels/{hotel_id}/rooms/{room_id}")
async def delete_hotel_room(
    hotel_id: str,
    room_id: str,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a hotel room (admin only)."""
    from ...models.mysql_models import HotelRoom

    try:
        room = db.query(HotelRoom).filter(
            HotelRoom.room_id == room_id,
            HotelRoom.hotel_id == hotel_id
        ).first()

        if not room:
            handle_not_found("Room", room_id)

        db.delete(room)
        db.commit()

        return {
            "message": f"Room {room_id} deleted successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting hotel room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete room: {str(e)}")


# ==================== Car Management ====================

@app.get("/cars")
async def get_all_cars(
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all cars (admin only)."""
    from ...models.mysql_models import Car
    from ...schemas.car_schemas import CarResponse

    try:
        cars = db.query(Car).order_by(Car.created_at.desc()).all()
        return {
            "cars": [CarResponse.model_validate(car) for car in cars]
        }
    except Exception as e:
        logger.error(f"Error getting cars: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get cars: {str(e)}")


@app.post("/cars")
async def create_car(
    car_data: str = Form(...),  # JSON string
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Create a new car listing (admin only) with optional image upload."""
    import json
    from ...services.car_service.service import CarService
    from ...schemas.car_schemas import CarCreate, CarResponse
    from .image_upload import save_uploaded_image

    try:
        # Parse JSON data
        data = json.loads(car_data)
        
        # Handle image upload
        image_url = None
        if image and image.filename:
            image_url = await save_uploaded_image(image, "car", data.get("car_id", ""))
            data["image_url"] = image_url
        
        car_create = CarCreate(**data)
        service = CarService(db)
        car = service.create_car(car_create)

        return {
            "message": "Car created successfully",
            "car": CarResponse.model_validate(car)
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating car: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create car: {str(e)}")


@app.put("/cars/{car_id}")
async def update_car(
    car_id: str,
    car_data: str = Form(...),  # JSON string
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update car information (admin only) with optional image upload."""
    import json
    from ...services.car_service.service import CarService
    from ...schemas.car_schemas import CarUpdate, CarResponse
    from .image_upload import save_uploaded_image, delete_image

    try:
        # Parse JSON data
        data = json.loads(car_data)
        
        # Handle image upload
        if image and image.filename:
            # Get old car to delete old image
            service = CarService(db)
            old_car = service.get_car(car_id)
            if old_car and old_car.image_url:
                delete_image(old_car.image_url)
            
            # Save new image
            image_url = await save_uploaded_image(image, "car", car_id)
            data["image_url"] = image_url
        
        car_update = CarUpdate(**data)
        car = service.update_car(car_id, car_update)

        if not car:
            handle_not_found("Car", car_id)

        return {
            "message": "Car updated successfully",
            "car": CarResponse.model_validate(car)
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating car: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update car: {str(e)}")


@app.delete("/cars/{car_id}")
async def delete_car(
    car_id: str,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a car listing (admin only)."""
    from ...services.car_service.service import CarService

    try:
        service = CarService(db)
        deleted = service.delete_car(car_id)

        if not deleted:
            handle_not_found("Car", car_id)

        return {
            "message": f"Car {car_id} deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting car: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete car: {str(e)}")


# ==================== Flight Management ====================

@app.get("/flights")
async def get_all_flights(
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all flights (admin only)."""
    from ...models.mysql_models import Flight
    from ...schemas.flight_schemas import FlightResponse

    try:
        flights = db.query(Flight).order_by(Flight.created_at.desc()).all()
        return {
            "flights": [FlightResponse.model_validate(flight) for flight in flights]
        }
    except Exception as e:
        logger.error(f"Error getting flights: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get flights: {str(e)}")


@app.post("/flights")
async def create_flight(
    flight_data: dict,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Create a new flight (admin only)."""
    from ...services.flight_service.service import FlightService
    from ...schemas.flight_schemas import FlightCreate, FlightResponse

    try:
        flight_create = FlightCreate(**flight_data)
        service = FlightService(db)
        flight = service.create_flight(flight_create)

        return {
            "message": "Flight created successfully",
            "flight": FlightResponse.model_validate(flight)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating flight: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create flight: {str(e)}")


@app.put("/flights/{flight_id}")
async def update_flight(
    flight_id: str,
    flight_data: dict,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update flight information (admin only)."""
    from ...services.flight_service.service import FlightService
    from ...schemas.flight_schemas import FlightUpdate, FlightResponse
    
    try:
        flight_update = FlightUpdate(**flight_data)
        service = FlightService(db)
        flight = service.update_flight(flight_id, flight_update)
        
        if not flight:
            handle_not_found("Flight", flight_id)
        
        return {
            "message": "Flight updated successfully",
            "flight": FlightResponse.model_validate(flight)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating flight: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update flight: {str(e)}")


@app.delete("/flights/{flight_id}")
async def delete_flight(
    flight_id: str,
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a flight (admin only)."""
    from ...services.flight_service.service import FlightService
    
    try:
        service = FlightService(db)
        deleted = service.delete_flight(flight_id)
        
        if not deleted:
            handle_not_found("Flight", flight_id)
        
        return {
            "message": f"Flight {flight_id} deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting flight: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete flight: {str(e)}")



# ==================== Admin Authentication ====================

@app.post("/auth/signup")
async def admin_signup(
    admin_data: str = Form(...),  # JSON string
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_mysql_session)
):
    """Create a new admin account with optional profile image upload."""
    import json
    from .service import AdminService
    from ...schemas.admin_schemas import AdminCreate
    from .image_upload import save_uploaded_image
    
    try:
        # Parse JSON data
        data = json.loads(admin_data)
        
        # Handle image upload
        image_url = None
        if image and image.filename:
            image_url = await save_uploaded_image(image, "admin", data.get("admin_id", ""))
            data["profile_image_url"] = image_url
        
        admin_create = AdminCreate(**data)
        service = AdminService(db)
        admin = service.create_admin(admin_create)
        
        from ...schemas.admin_schemas import AdminResponse
        return {
            "message": "Admin account created successfully",
            "admin": AdminResponse.model_validate(admin)
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Error creating admin: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create admin account: {str(e)}")


@app.post("/auth/login")
async def admin_login(
    login: AdminLogin,
    db: Session = Depends(get_mysql_session)
):
    """Admin login."""
    from .service import AdminService
    from .auth import create_admin_access_token
    from ...schemas.admin_schemas import AdminResponse, AdminTokenResponse
    
    try:
        service = AdminService(db)
        admin = service.authenticate_admin(login.email, login.password)
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        # admin.role is now a string (not enum) since we changed the column type
        role_value = str(admin.role).upper() if admin.role else 'ADMIN'
        access_token = create_admin_access_token(
            data={"sub": admin.admin_id, "role": role_value.lower()}
        )
        
        return AdminTokenResponse(
            access_token=access_token,
            admin=AdminResponse.model_validate(admin)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during admin login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.put("/listings/flight/{flight_id}/price")
async def update_flight_price(
    flight_id: str,
    base_price: float = Query(..., ge=0, description="New base price"),
    db: Session = Depends(get_mysql_session),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update flight price (admin only)."""
    from ...services.flight_service.service import FlightService
    from ...schemas.flight_schemas import FlightUpdate
    from ...common.websocket_manager import PriceUpdateManager
    from decimal import Decimal
    
    service = FlightService(db)
    
    # Get old price before update
    old_flight = service.get_flight(flight_id)
    if not old_flight:
        handle_not_found("Flight", flight_id)
    
    old_price = float(old_flight.base_price) if old_flight.base_price else None
    
    # Update flight price
    flight_update = FlightUpdate(base_price=Decimal(str(base_price)))
    flight = service.update_flight(flight_id, flight_update)
    
    if not flight:
        handle_not_found("Flight", flight_id)
    
    # Broadcast price update via WebSocket
    new_price = float(flight.base_price) if flight.base_price else None
    try:
        manager = PriceUpdateManager()
        await manager.broadcast_price_update(
            listing_id=flight_id,
            listing_type="flight",
            new_price=new_price,
            old_price=old_price
        )
        logger.info(f"Broadcasted price update for flight {flight_id}: ${old_price} -> ${new_price}")
    except Exception as e:
        logger.warning(f"Failed to broadcast price update: {e}")
    
    return {
        "flight_id": flight.flight_id,
        "base_price": float(flight.base_price),
        "old_price": old_price,
        "message": "Price updated successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)

