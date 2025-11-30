"""
Admin Service - FastAPI Routes
REST API endpoints for admin operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from .models import (
    AdminCreate, AdminUpdate, AdminResponse, AdminListResponse, AdminRole,
    AdminLogin, AdminTokenResponse, AdminPermissions,
    ListingCreate, ListingUpdate, ListingResponse, ListingType,
    TopPropertiesReport, CityRevenueReport, ProviderReport,
    MessageResponse, ErrorResponse, ActionType
)
from .service import AdminService, AuthenticationError, AuthorizationError
from .repository import DuplicateAdminError, AdminNotFoundError
from shared.database import get_db
from shared.validators import InvalidZipCodeError, MalformedStateError

logger = logging.getLogger(__name__)

# Create routers
router = APIRouter(prefix="/admin", tags=["Admin"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login", auto_error=False)


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Dependency to get AdminService instance"""
    return AdminService(db)


async def get_current_admin(
    token: Optional[str] = Depends(oauth2_scheme),
    service: AdminService = Depends(get_admin_service)
):
    """Dependency to get current authenticated admin"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    admin = service.get_admin_from_token(token)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return admin


def require_permission(permission: str):
    """Decorator to require specific permission"""
    async def permission_checker(
        current_admin = Depends(get_current_admin),
        service: AdminService = Depends(get_admin_service)
    ):
        if not service.check_permission(current_admin, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_admin
    return permission_checker


# ========================================
# Authentication Endpoints
# ========================================

@router.post(
    "/login",
    response_model=AdminTokenResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Admin login",
    description="Authenticate admin and get access token."
)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AdminService = Depends(get_admin_service)
):
    """Admin login with email and password."""
    try:
        admin = service.authenticate_admin(form_data.username, form_data.password)
        token, expires_in = service.create_access_token(admin)
        
        admin_dict = admin.to_dict()
        
        return AdminTokenResponse(
            access_token=token,
            expires_in=expires_in,
            admin=AdminResponse(
                **{k: v for k, v in admin_dict.items() if k != 'permissions'},
                permissions=AdminPermissions(**admin_dict['permissions'])
            )
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/login/json",
    response_model=AdminTokenResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Admin login (JSON)",
    description="Authenticate admin with JSON body."
)
async def admin_login_json(
    login_data: AdminLogin,
    service: AdminService = Depends(get_admin_service)
):
    """Admin login with JSON format."""
    try:
        admin = service.authenticate_admin(login_data.email, login_data.password)
        token, expires_in = service.create_access_token(admin)
        
        admin_dict = admin.to_dict()
        
        return AdminTokenResponse(
            access_token=token,
            expires_in=expires_in,
            admin=AdminResponse(
                **{k: v for k, v in admin_dict.items() if k != 'permissions'},
                permissions=AdminPermissions(**admin_dict['permissions'])
            )
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# ========================================
# Admin CRUD Endpoints
# ========================================

@router.get(
    "/me",
    response_model=AdminResponse,
    summary="Get current admin profile"
)
async def get_current_admin_profile(
    current_admin = Depends(get_current_admin)
):
    """Get current authenticated admin's profile."""
    admin_dict = current_admin.to_dict()
    return AdminResponse(
        **{k: v for k, v in admin_dict.items() if k != 'permissions'},
        permissions=AdminPermissions(**admin_dict['permissions'])
    )


@router.post(
    "/admins",
    response_model=AdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new admin",
    description="Create a new admin account. Requires manage_admins permission."
)
async def create_admin(
    admin_data: AdminCreate,
    request: Request,
    current_admin = Depends(require_permission("manage_admins")),
    service: AdminService = Depends(get_admin_service)
):
    """Create a new admin account."""
    try:
        admin = service.create_admin(admin_data, created_by=current_admin.admin_id)
        
        # Log activity
        service.log_activity(
            admin_id=current_admin.admin_id,
            action_type=ActionType.CREATE_ADMIN,
            entity_type="admin",
            entity_id=admin.admin_id,
            ip_address=request.client.host if request.client else None
        )
        
        admin_dict = admin.to_dict()
        return AdminResponse(
            **{k: v for k, v in admin_dict.items() if k != 'permissions'},
            permissions=AdminPermissions(**admin_dict['permissions'])
        )
    except DuplicateAdminError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "/admins/{admin_id}",
    response_model=AdminResponse,
    summary="Get admin by ID"
)
async def get_admin(
    admin_id: str,
    current_admin = Depends(require_permission("manage_admins")),
    service: AdminService = Depends(get_admin_service)
):
    """Get admin by ID."""
    admin = service.get_admin(admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin with ID {admin_id} not found"
        )
    
    admin_dict = admin.to_dict()
    return AdminResponse(
        **{k: v for k, v in admin_dict.items() if k != 'permissions'},
        permissions=AdminPermissions(**admin_dict['permissions'])
    )


@router.put(
    "/admins/{admin_id}",
    response_model=AdminResponse,
    summary="Update admin"
)
async def update_admin(
    admin_id: str,
    update_data: AdminUpdate,
    request: Request,
    current_admin = Depends(require_permission("manage_admins")),
    service: AdminService = Depends(get_admin_service)
):
    """Update admin information."""
    try:
        admin = service.update_admin(admin_id, update_data)
        
        # Log activity
        service.log_activity(
            admin_id=current_admin.admin_id,
            action_type=ActionType.UPDATE_ADMIN,
            entity_type="admin",
            entity_id=admin_id,
            ip_address=request.client.host if request.client else None
        )
        
        admin_dict = admin.to_dict()
        return AdminResponse(
            **{k: v for k, v in admin_dict.items() if k != 'permissions'},
            permissions=AdminPermissions(**admin_dict['permissions'])
        )
    except AdminNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateAdminError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete(
    "/admins/{admin_id}",
    response_model=MessageResponse,
    summary="Delete admin"
)
async def delete_admin(
    admin_id: str,
    request: Request,
    current_admin = Depends(require_permission("manage_admins")),
    service: AdminService = Depends(get_admin_service)
):
    """Delete an admin account."""
    try:
        service.delete_admin(admin_id)
        
        # Log activity
        service.log_activity(
            admin_id=current_admin.admin_id,
            action_type=ActionType.DELETE_ADMIN,
            entity_type="admin",
            entity_id=admin_id,
            ip_address=request.client.host if request.client else None
        )
        
        return MessageResponse(message=f"Admin {admin_id} deleted successfully")
    except AdminNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/admins",
    response_model=AdminListResponse,
    summary="List admins"
)
async def list_admins(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[AdminRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_admin = Depends(require_permission("manage_admins")),
    service: AdminService = Depends(get_admin_service)
):
    """List admins with pagination and filtering."""
    admins, total = service.list_admins(
        page=page,
        page_size=page_size,
        role=role,
        is_active=is_active,
        search=search
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    admin_responses = []
    for admin in admins:
        admin_dict = admin.to_dict()
        admin_responses.append(AdminResponse(
            **{k: v for k, v in admin_dict.items() if k != 'permissions'},
            permissions=AdminPermissions(**admin_dict['permissions'])
        ))
    
    return AdminListResponse(
        admins=admin_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ========================================
# User Management Endpoints (Admin)
# ========================================

@router.get(
    "/users",
    summary="List all users (Admin)",
    description="View all users in the system. Requires manage_users permission."
)
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: Optional[str] = None,
    city: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_admin = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db)
):
    """List all users for admin management."""
    # Import here to avoid circular imports
    from backend.user_service.service import UserService
    
    user_service = UserService(db)
    users, total = user_service.list_users(
        page=page,
        page_size=page_size,
        state=state,
        city=city,
        is_active=is_active,
        search=search
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "users": [u.to_dict() for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.put(
    "/users/{user_id}",
    summary="Modify user account (Admin)",
    description="Modify a user account. Requires manage_users permission."
)
async def admin_update_user(
    user_id: str,
    update_data: dict,
    request: Request,
    current_admin = Depends(require_permission("manage_users")),
    service: AdminService = Depends(get_admin_service),
    db: Session = Depends(get_db)
):
    """Modify a user account as admin."""
    from backend.user_service.service import UserService
    from backend.user_service.models import UserUpdate
    
    user_service = UserService(db)
    
    try:
        user_update = UserUpdate(**update_data)
        user = user_service.update_user(user_id, user_update)
        
        # Log activity
        service.log_activity(
            admin_id=current_admin.admin_id,
            action_type=ActionType.UPDATE_USER,
            entity_type="user",
            entity_id=user_id,
            details={"fields_updated": list(update_data.keys())},
            ip_address=request.client.host if request.client else None
        )
        
        return user.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
    summary="Delete user account (Admin)"
)
async def admin_delete_user(
    user_id: str,
    request: Request,
    current_admin = Depends(require_permission("manage_users")),
    service: AdminService = Depends(get_admin_service),
    db: Session = Depends(get_db)
):
    """Delete a user account as admin."""
    from backend.user_service.service import UserService
    
    user_service = UserService(db)
    
    try:
        user_service.delete_user(user_id)
        
        # Log activity
        service.log_activity(
            admin_id=current_admin.admin_id,
            action_type=ActionType.DELETE_USER,
            entity_type="user",
            entity_id=user_id,
            ip_address=request.client.host if request.client else None
        )
        
        return MessageResponse(message=f"User {user_id} deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ========================================
# Listing Management Endpoints
# ========================================

@router.post(
    "/listings",
    response_model=ListingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new listing",
    description="Add a new hotel/flight/car listing. Requires manage_listings permission."
)
async def create_listing(
    listing_data: ListingCreate,
    request: Request,
    current_admin = Depends(require_permission("manage_listings")),
    service: AdminService = Depends(get_admin_service)
):
    """Create a new listing (hotel/flight/car)."""
    # This would integrate with the Listings service (Team 2)
    # For now, return a mock response
    service.log_activity(
        admin_id=current_admin.admin_id,
        action_type=ActionType.CREATE_LISTING,
        entity_type=listing_data.listing_type.value,
        details={"name": listing_data.name},
        ip_address=request.client.host if request.client else None
    )
    
    return ListingResponse(
        listing_id="new-listing-id",
        listing_type=listing_data.listing_type,
        name=listing_data.name,
        description=listing_data.description,
        price=listing_data.price,
        is_active=listing_data.is_active,
        details=listing_data.details,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.get(
    "/listings",
    summary="Search listings (Admin)",
    description="Search for listings. Requires manage_listings permission."
)
async def search_listings(
    listing_type: Optional[ListingType] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin = Depends(require_permission("manage_listings"))
):
    """Search listings for admin management."""
    # This would integrate with the Listings service (Team 2)
    return {
        "listings": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": 0
    }


@router.put(
    "/listings/{listing_id}",
    response_model=ListingResponse,
    summary="Edit listing"
)
async def update_listing(
    listing_id: str,
    update_data: ListingUpdate,
    request: Request,
    current_admin = Depends(require_permission("manage_listings")),
    service: AdminService = Depends(get_admin_service)
):
    """Update a listing."""
    service.log_activity(
        admin_id=current_admin.admin_id,
        action_type=ActionType.UPDATE_LISTING,
        entity_type="listing",
        entity_id=listing_id,
        ip_address=request.client.host if request.client else None
    )
    
    # This would integrate with the Listings service (Team 2)
    return ListingResponse(
        listing_id=listing_id,
        listing_type=ListingType.HOTEL,
        name=update_data.name or "Updated Listing",
        description=update_data.description,
        price=update_data.price or 0,
        is_active=update_data.is_active if update_data.is_active is not None else True,
        details=update_data.details or {},
        updated_at=datetime.utcnow()
    )


# ========================================
# Analytics and Reports Endpoints
# ========================================

@router.get(
    "/reports/top-properties",
    response_model=TopPropertiesReport,
    summary="Top 10 properties by revenue",
    description="Get top 10 properties with revenue per year."
)
async def get_top_properties_report(
    year: int = Query(None, description="Year for report"),
    request: Request = None,
    current_admin = Depends(require_permission("view_analytics")),
    service: AdminService = Depends(get_admin_service)
):
    """Get top 10 properties with revenue per year."""
    service.log_activity(
        admin_id=current_admin.admin_id,
        action_type=ActionType.VIEW_REPORT,
        details={"report_type": "top_properties", "year": year},
        ip_address=request.client.host if request.client else None
    )
    
    return service.get_top_properties_report(year)


@router.get(
    "/reports/city-revenue",
    response_model=CityRevenueReport,
    summary="City-wise revenue",
    description="Get city-wise revenue per year."
)
async def get_city_revenue_report(
    year: int = Query(None, description="Year for report"),
    request: Request = None,
    current_admin = Depends(require_permission("view_analytics")),
    service: AdminService = Depends(get_admin_service)
):
    """Get city-wise revenue per year."""
    service.log_activity(
        admin_id=current_admin.admin_id,
        action_type=ActionType.VIEW_REPORT,
        details={"report_type": "city_revenue", "year": year},
        ip_address=request.client.host if request.client else None
    )
    
    return service.get_city_revenue_report(year)


@router.get(
    "/reports/provider-analysis",
    response_model=ProviderReport,
    summary="Top providers analysis",
    description="Get top 10 providers with maximum properties sold."
)
async def get_provider_report(
    month: int = Query(None, ge=1, le=12, description="Month (1-12)"),
    year: int = Query(None, description="Year"),
    request: Request = None,
    current_admin = Depends(require_permission("view_analytics")),
    service: AdminService = Depends(get_admin_service)
):
    """Get top 10 providers with maximum properties sold."""
    service.log_activity(
        admin_id=current_admin.admin_id,
        action_type=ActionType.VIEW_REPORT,
        details={"report_type": "provider_analysis", "month": month, "year": year},
        ip_address=request.client.host if request.client else None
    )
    
    return service.get_provider_report(month, year)


@router.get(
    "/dashboard/stats",
    summary="Dashboard statistics",
    description="Get dashboard statistics for admin."
)
async def get_dashboard_stats(
    current_admin = Depends(require_permission("view_analytics")),
    service: AdminService = Depends(get_admin_service)
):
    """Get admin dashboard statistics."""
    return service.get_dashboard_stats()


@router.get(
    "/activity-log",
    summary="Admin activity log",
    description="Get admin activity log."
)
async def get_activity_log(
    admin_id: Optional[str] = None,
    action_type: Optional[ActionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_admin = Depends(require_permission("view_analytics")),
    service: AdminService = Depends(get_admin_service)
):
    """Get admin activity log."""
    logs, total = service.get_activity_log(
        admin_id=admin_id,
        action_type=action_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
    
    return {
        "logs": [
            {
                "log_id": log.log_id,
                "admin_id": log.admin_id,
                "action_type": log.action_type.value,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


