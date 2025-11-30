"""
User Service - FastAPI Routes
REST API endpoints for user operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import logging

from .models import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserLogin, TokenResponse, MessageResponse, ErrorResponse
)
from .service import UserService, AuthenticationError
from .repository import DuplicateUserError, UserNotFoundError
from shared.database import get_db
from shared.validators import (
    InvalidSSNError, InvalidZipCodeError, MalformedStateError, InvalidUserIdError
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get UserService instance"""
    return UserService(db)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service)
):
    """Dependency to get current authenticated user"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = service.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


# ========================================
# User CRUD Endpoints
# ========================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "User already exists"}
    },
    summary="Create a new user",
    description="Register a new user with SSN-format ID. Validates SSN, ZIP code, and state."
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    Create a new user account.
    
    - **user_id**: Must be in SSN format (###-##-####)
    - **zip_code**: Must be in format ##### or #####-####
    - **state**: Must be a valid US state abbreviation or name
    """
    try:
        user = service.create_user(user_data)
        return UserResponse(**user.to_dict(mask_sensitive=True))
    except DuplicateUserError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (InvalidSSNError, InvalidZipCodeError, MalformedStateError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        400: {"model": ErrorResponse, "description": "Invalid user ID format"}
    },
    summary="Get user by ID",
    description="Retrieve user information by their SSN-format ID."
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Get user by ID.
    
    - **user_id**: User ID in SSN format (###-##-####)
    """
    try:
        # Validate user ID format
        from shared.validators import validate_user_id
        validate_user_id(user_id)
        
        user = service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return UserResponse(**user.to_dict(mask_sensitive=True))
    except InvalidUserIdError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Email already exists"}
    },
    summary="Update user information",
    description="Update any user attribute. All fields are optional."
)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    """
    Update user information.
    
    - All fields are optional
    - Only provided fields will be updated
    - Validates ZIP code and state if provided
    """
    try:
        user = service.update_user(user_id, update_data)
        return UserResponse(**user.to_dict(mask_sensitive=True))
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateUserError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (InvalidZipCodeError, MalformedStateError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"}
    },
    summary="Delete a user",
    description="Permanently delete a user account."
)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Delete a user account.
    
    - **user_id**: User ID in SSN format
    """
    try:
        service.delete_user(user_id)
        return MessageResponse(message=f"User {user_id} deleted successfully")
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ========================================
# User List and Search
# ========================================

@router.get(
    "",
    response_model=UserListResponse,
    summary="List users with pagination",
    description="Get paginated list of users with optional filtering."
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    state: Optional[str] = Query(None, description="Filter by state abbreviation"),
    city: Optional[str] = Query(None, description="Filter by city"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and email"),
    service: UserService = Depends(get_user_service)
):
    """
    List users with pagination and filtering.
    
    - Supports filtering by state, city, active status
    - Supports search in name and email
    """
    users, total = service.list_users(
        page=page,
        page_size=page_size,
        state=state,
        city=city,
        is_active=is_active,
        search=search
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return UserListResponse(
        users=[UserResponse(**u.to_dict(mask_sensitive=True)) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ========================================
# Authentication Endpoints
# ========================================

@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    },
    summary="User login",
    description="Authenticate user and get access token."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
):
    """
    User login with email and password.
    
    Returns JWT access token for authenticated requests.
    """
    try:
        user = service.authenticate_user(form_data.username, form_data.password)
        token, expires_in = service.create_access_token(user)
        
        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user=UserResponse(**user.to_dict(mask_sensitive=True))
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/login/json",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    },
    summary="User login (JSON)",
    description="Authenticate user with JSON body."
)
async def login_json(
    login_data: UserLogin,
    service: UserService = Depends(get_user_service)
):
    """
    User login with email and password (JSON format).
    """
    try:
        user = service.authenticate_user(login_data.email, login_data.password)
        token, expires_in = service.create_access_token(user)
        
        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user=UserResponse(**user.to_dict(mask_sensitive=True))
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# ========================================
# Profile Management
# ========================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user."
)
async def get_current_user_profile(
    current_user = Depends(get_current_user)
):
    """Get current authenticated user's profile."""
    return UserResponse(**current_user.to_dict(mask_sensitive=True))


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update the profile of the currently authenticated user."
)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Update current user's profile."""
    try:
        user = service.update_user(current_user.user_id, update_data)
        return UserResponse(**user.to_dict(mask_sensitive=True))
    except (InvalidZipCodeError, MalformedStateError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid current password"}
    },
    summary="Change password",
    description="Change the current user's password."
)
async def change_password(
    current_password: str,
    new_password: str,
    current_user = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Change current user's password."""
    try:
        service.change_password(
            current_user.user_id,
            current_password,
            new_password
        )
        return MessageResponse(message="Password changed successfully")
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{user_id}/profile-image",
    response_model=UserResponse,
    summary="Upload profile image",
    description="Upload or update user's profile image."
)
async def upload_profile_image(
    user_id: str,
    file: UploadFile = File(...),
    service: UserService = Depends(get_user_service)
):
    """
    Upload profile image.
    
    Accepts JPEG, PNG, GIF, or WebP images up to 5MB.
    """
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, WebP"
        )
    
    # Validate file size (5MB max)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 5MB"
        )
    
    # TODO: Upload to S3 or local storage
    # For now, just return a placeholder URL
    image_url = f"/uploads/profiles/{user_id}/{file.filename}"
    
    try:
        user = service.update_profile_image(user_id, image_url)
        return UserResponse(**user.to_dict(mask_sensitive=True))
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ========================================
# Statistics
# ========================================

@router.get(
    "/stats/summary",
    summary="Get user statistics",
    description="Get summary statistics about users."
)
async def get_user_stats(
    service: UserService = Depends(get_user_service)
):
    """Get user statistics summary."""
    return service.get_user_stats()


