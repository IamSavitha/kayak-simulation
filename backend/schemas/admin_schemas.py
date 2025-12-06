"""
Pydantic schemas for Admin-related requests and responses.
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

from ..models.mysql_models import AdminRole


class AdminCreate(BaseModel):
    """Schema for creating a new admin."""
    admin_id: str = Field(..., max_length=50, description="Admin ID (e.g., ADMIN-001)")
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=8)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    profile_image_url: Optional[str] = Field(None, max_length=500, description="URL to admin profile image")
    role: AdminRole = Field(default=AdminRole.ADMIN)
    
    @field_validator('admin_id')
    @classmethod
    def validate_admin_id(cls, v):
        if not v.startswith('ADMIN-'):
            raise ValueError('Admin ID must start with "ADMIN-"')
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "admin_id": "ADMIN-001",
                "first_name": "John",
                "last_name": "Admin",
                "email": "admin@kayak.com",
                "phone_number": "555-1234",
                "password": "admin123",
                "address": "123 Admin St",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94102",
                "role": "admin"
            }
        }


class AdminUpdate(BaseModel):
    """Schema for updating admin information."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    profile_image_url: Optional[str] = Field(None, max_length=500)
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None


class AdminLogin(BaseModel):
    """Schema for admin login."""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@kayak.com",
                "password": "admin123"
            }
        }


class AdminResponse(BaseModel):
    """Schema for admin response."""
    admin_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    profile_image_url: Optional[str] = None
    role: AdminRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminTokenResponse(BaseModel):
    """Schema for admin token response."""
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse

