"""
Admin Service - Pydantic Models and SQLAlchemy ORM Models
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator, EmailStr
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Integer, JSON, ForeignKey
from sqlalchemy.sql import func
from enum import Enum
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Base
from shared.validators import validate_zip_code, validate_state


# ========================================
# Enums
# ========================================

class AdminRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    ANALYST = "ANALYST"


class ActionType(str, Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE_USER = "CREATE_USER"
    UPDATE_USER = "UPDATE_USER"
    DELETE_USER = "DELETE_USER"
    CREATE_LISTING = "CREATE_LISTING"
    UPDATE_LISTING = "UPDATE_LISTING"
    DELETE_LISTING = "DELETE_LISTING"
    VIEW_BILLING = "VIEW_BILLING"
    MODIFY_BILLING = "MODIFY_BILLING"
    VIEW_REPORT = "VIEW_REPORT"
    EXPORT_REPORT = "EXPORT_REPORT"
    CREATE_ADMIN = "CREATE_ADMIN"
    UPDATE_ADMIN = "UPDATE_ADMIN"
    DELETE_ADMIN = "DELETE_ADMIN"


# ========================================
# SQLAlchemy ORM Models
# ========================================

class AdminORM(Base):
    """SQLAlchemy ORM model for administrators table"""
    __tablename__ = "administrators"
    
    admin_id = Column(String(36), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    role = Column(SQLEnum(AdminRole), nullable=False, default=AdminRole.ADMIN)
    access_level = Column(Integer, nullable=False, default=1)
    
    can_manage_users = Column(Boolean, default=True)
    can_manage_listings = Column(Boolean, default=True)
    can_view_billing = Column(Boolean, default=True)
    can_view_analytics = Column(Boolean, default=True)
    can_manage_admins = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    created_by = Column(String(36), ForeignKey("administrators.admin_id"), nullable=True)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "admin_id": self.admin_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "role": self.role.value if self.role else None,
            "access_level": self.access_level,
            "permissions": {
                "can_manage_users": self.can_manage_users,
                "can_manage_listings": self.can_manage_listings,
                "can_view_billing": self.can_view_billing,
                "can_view_analytics": self.can_view_analytics,
                "can_manage_admins": self.can_manage_admins
            },
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }


class AdminActivityLogORM(Base):
    """SQLAlchemy ORM model for admin activity log"""
    __tablename__ = "admin_activity_log"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(String(36), ForeignKey("administrators.admin_id"), nullable=False)
    action_type = Column(SQLEnum(ActionType), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AdminSessionORM(Base):
    """SQLAlchemy ORM model for admin sessions"""
    __tablename__ = "admin_sessions"
    
    session_id = Column(String(36), primary_key=True)
    admin_id = Column(String(36), ForeignKey("administrators.admin_id"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)


# ========================================
# Pydantic Models for API
# ========================================

class AdminPermissions(BaseModel):
    """Admin permissions model"""
    can_manage_users: bool = True
    can_manage_listings: bool = True
    can_view_billing: bool = True
    can_view_analytics: bool = True
    can_manage_admins: bool = False


class AdminCreate(BaseModel):
    """Model for creating a new admin"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    zip_code: str
    password: str = Field(..., min_length=8, max_length=100)
    role: AdminRole = AdminRole.ADMIN
    access_level: int = Field(1, ge=1, le=10)
    permissions: Optional[AdminPermissions] = None
    
    @field_validator('state')
    @classmethod
    def validate_state_field(cls, v):
        return validate_state(v)
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code_field(cls, v):
        validate_zip_code(v)
        return v


class AdminUpdate(BaseModel):
    """Model for updating admin information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=50)
    zip_code: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[AdminRole] = None
    access_level: Optional[int] = Field(None, ge=1, le=10)
    permissions: Optional[AdminPermissions] = None
    is_active: Optional[bool] = None
    
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


class AdminResponse(BaseModel):
    """Model for admin response"""
    admin_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    address: str
    city: str
    state: str
    zip_code: str
    role: str
    access_level: int
    permissions: AdminPermissions
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminListResponse(BaseModel):
    """Model for paginated admin list response"""
    admins: List[AdminResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminLogin(BaseModel):
    """Model for admin login request"""
    email: EmailStr
    password: str


class AdminTokenResponse(BaseModel):
    """Model for admin authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: AdminResponse


# ========================================
# Listing Management Models
# ========================================

class ListingType(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    CAR = "car"


class ListingBase(BaseModel):
    """Base model for listings"""
    listing_type: ListingType
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    is_active: bool = True


class ListingCreate(ListingBase):
    """Model for creating a listing"""
    details: dict = Field(default_factory=dict)


class ListingUpdate(BaseModel):
    """Model for updating a listing"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    details: Optional[dict] = None


class ListingResponse(ListingBase):
    """Model for listing response"""
    listing_id: str
    details: dict
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========================================
# Analytics and Reports Models
# ========================================

class RevenueByProperty(BaseModel):
    """Revenue by property for reports"""
    property_id: str
    property_name: str
    revenue: float
    booking_count: int


class RevenueByCity(BaseModel):
    """Revenue by city for reports"""
    city: str
    state: str
    revenue: float
    booking_count: int


class ProviderAnalytics(BaseModel):
    """Provider/Host analytics"""
    provider_id: str
    provider_name: str
    properties_sold: int
    revenue: float


class TopPropertiesReport(BaseModel):
    """Top 10 properties revenue report"""
    year: int
    properties: List[RevenueByProperty]
    total_revenue: float


class CityRevenueReport(BaseModel):
    """City-wise revenue report"""
    year: int
    cities: List[RevenueByCity]
    total_revenue: float


class ProviderReport(BaseModel):
    """Top providers report"""
    month: str
    year: int
    providers: List[ProviderAnalytics]


class AdminActivityLog(BaseModel):
    """Admin activity log entry"""
    log_id: int
    admin_id: str
    admin_name: str
    action_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime


# ========================================
# Common Response Models
# ========================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


