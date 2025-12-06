"""
Image upload utilities for admin service.
"""
import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Base directory for uploaded images
UPLOAD_DIR = Path("static/uploads")
HOTEL_IMAGES_DIR = UPLOAD_DIR / "hotels"
CAR_IMAGES_DIR = UPLOAD_DIR / "cars"
USER_PROFILE_IMAGES_DIR = UPLOAD_DIR / "users"
ADMIN_PROFILE_IMAGES_DIR = UPLOAD_DIR / "admins"

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_directories():
    """Ensure upload directories exist."""
    HOTEL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CAR_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    USER_PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    ADMIN_PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def is_valid_image(file: UploadFile) -> bool:
    """Check if uploaded file is a valid image."""
    if not file.filename:
        return False
    
    ext = Path(file.filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


async def save_uploaded_image(
    file: UploadFile,
    entity_type: str,  # "hotel", "car", "user", or "admin"
    entity_id: str
) -> str:
    """
    Save uploaded image and return the URL path.
    
    Args:
        file: Uploaded file
        entity_type: Type of entity ("hotel" or "car")
        entity_id: ID of the entity
    
    Returns:
        URL path to the saved image (e.g., "/static/uploads/hotels/HOTEL-001-abc123.jpg")
    """
    ensure_directories()
    
    # Validate file
    if not is_valid_image(file):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{entity_id}-{unique_id}{ext}"
    
    # Determine upload directory
    if entity_type == "hotel":
        upload_dir = HOTEL_IMAGES_DIR
    elif entity_type == "car":
        upload_dir = CAR_IMAGES_DIR
    elif entity_type == "user":
        upload_dir = USER_PROFILE_IMAGES_DIR
    elif entity_type == "admin":
        upload_dir = ADMIN_PROFILE_IMAGES_DIR
    else:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")
    
    # Save file
    file_path = upload_dir / filename
    try:
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return URL path (relative to static root)
        return f"/static/uploads/{entity_type}s/{filename}"
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        raise HTTPException(status_code=500, detail="Failed to save image")


def delete_image(image_url: Optional[str]) -> bool:
    """
    Delete an image file.
    
    Args:
        image_url: URL path to the image
    
    Returns:
        True if deleted, False if not found or error
    """
    if not image_url:
        return False
    
    try:
        # Extract file path from URL
        if image_url.startswith("/static/"):
            file_path = Path(image_url.lstrip("/"))
        else:
            file_path = Path(image_url)
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        return False

