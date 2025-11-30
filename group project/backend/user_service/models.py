"""
User Service - Pydantic Models and SQLAlchemy ORM Models
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, EmailStr
from sqlalchemy import Column, String, Boolean, DateTime, Text, CHAR, Integer
from sqlalchemy.sql import func
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Base
from shared.validators import (
    validate_ssn, validate_zip_code, validate_state, validate_email,
    US_STATES, InvalidSSNError, InvalidZipCodeError, MalformedStateError
)


# ========================================
# SQLAlchemy ORM Models
# ========================================

class UserORM(Base):
    """SQLAlchemy ORM model for users table"""
    __tablename__ = "users"
    
    user_id = Column(String(11), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(CHAR(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    profile_image_url = Column(String(500), nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Credit card details
    credit_card_number_encrypted = Column(String(500), nullable=True)
    credit_card_last_four = Column(CHAR(4), nullable=True)
    credit_card_expiry = Column(String(7), nullable=True)
    credit_card_type = Column(String(20), nullable=True)
    billing_address = Column(String(255), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(CHAR(2), nullable=True)
    billing_zip_code = Column(String(10), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    
    def to_dict(self, mask_sensitive: bool = True) -> dict:
        """Convert to dictionary, optionally masking sensitive data"""
        data = {
            "user_id": f"***-**-{self.user_id[-4:]}" if mask_sensitive else self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "profile_image_url": self.profile_image_url,
            "credit_card_masked": f"****-****-****-{self.credit_card_last_four}" if self.credit_card_last_four else None,
            "credit_card_type": self.credit_card_type,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
        return data


# ========================================
# Pydantic Models for API
# ========================================

class CreditCardInfo(BaseModel):
    """Credit card information model"""
    card_number: str = Field(..., min_length=13, max_length=19)
    expiry_date: str = Field(..., pattern=r'^(0[1-9]|1[0-2])\/20[2-9][0-9]$')  # MM/YYYY
    card_type: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_zip_code: Optional[str] = None
    
    @field_validator('billing_state')
    @classmethod
    def validate_billing_state(cls, v):
        if v:
            validate_state(v)
        return v
    
    @field_validator('billing_zip_code')
    @classmethod
    def validate_billing_zip(cls, v):
        if v:
            validate_zip_code(v)
        return v


class UserCreate(BaseModel):
    """Model for creating a new user"""
    user_id: str = Field(
        ..., 
        description="User ID in SSN format: ###-##-####",
        pattern=r'^[0-9]{3}-[0-9]{2}-[0-9]{4}$'
    )
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    zip_code: str = Field(..., description="Format: ##### or #####-####")
    password: str = Field(..., min_length=8, max_length=100)
    profile_image_url: Optional[str] = None
    credit_card: Optional[CreditCardInfo] = None
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not re.match(r'^[0-9]{3}-[0-9]{2}-[0-9]{4}$', v):
            raise ValueError('Invalid SSN format. Expected: ###-##-####')
        return v
    
    @field_validator('state')
    @classmethod
    def validate_state_field(cls, v):
        return validate_state(v)
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code_field(cls, v):
        validate_zip_code(v)
        return v
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        cleaned = re.sub(r'[\s\-\(\)\.]', '', v)
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise ValueError('Invalid phone number. Expected 10-digit US phone number.')
        return v


class UserUpdate(BaseModel):
    """Model for updating user information - all fields optional"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=50)
    zip_code: Optional[str] = None
    profile_image_url: Optional[str] = None
    credit_card: Optional[CreditCardInfo] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @field_validator('state')
    @classmethod
    def validate_state_field(cls, v):
        if v:
            return validate_state(v)
        return v
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code_field(cls, v):
        if v:
            validate_zip_code(v)
        return v
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r'[\s\-\(\)\.]', '', v)
            if not cleaned.isdigit() or len(cleaned) != 10:
                raise ValueError('Invalid phone number. Expected 10-digit US phone number.')
        return v


class UserResponse(BaseModel):
    """Model for user response (public data)"""
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    address: str
    city: str
    state: str
    zip_code: str
    profile_image_url: Optional[str] = None
    credit_card_masked: Optional[str] = None
    credit_card_type: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Model for paginated user list response"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserLogin(BaseModel):
    """Model for user login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Model for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


