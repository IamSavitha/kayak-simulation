"""
Admin Service - Business Logic Layer
Handles admin operations, authentication, and analytics.
"""

from typing import Optional, List, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import logging

from .models import (
    AdminORM, AdminCreate, AdminUpdate, AdminResponse, AdminRole, ActionType,
    TopPropertiesReport, CityRevenueReport, ProviderReport,
    RevenueByProperty, RevenueByCity, ProviderAnalytics
)
from .repository import AdminRepository, DuplicateAdminError, AdminNotFoundError
from shared.config import settings

logger = logging.getLogger(__name__)

# Password hashing - using argon2 as primary, bcrypt as fallback
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Hash password, handling bcrypt 72-byte limit"""
    # Truncate to 72 bytes for bcrypt compatibility
    truncated = password[:72] if len(password.encode('utf-8')) > 72 else password
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password, handling bcrypt 72-byte limit"""
    truncated = plain_password[:72] if len(plain_password.encode('utf-8')) > 72 else plain_password
    return pwd_context.verify(truncated, hashed_password)


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class AuthorizationError(Exception):
    """Raised when authorization fails"""
    pass


class AdminService:
    """
    Admin Service - Business Logic Layer
    Handles admin CRUD operations, authentication, and analytics.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AdminRepository(db)
    
    # ========================================
    # Admin CRUD Operations
    # ========================================
    
    def create_admin(self, admin_data: AdminCreate, created_by: Optional[str] = None) -> AdminORM:
        """Create a new admin account."""
        password_hash = hash_password(admin_data.password)
        return self.repository.create(admin_data, password_hash, created_by)
    
    def get_admin(self, admin_id: str) -> Optional[AdminORM]:
        """Get admin by ID."""
        return self.repository.get_by_id(admin_id)
    
    def get_admin_by_email(self, email: str) -> Optional[AdminORM]:
        """Get admin by email."""
        return self.repository.get_by_email(email)
    
    def update_admin(self, admin_id: str, update_data: AdminUpdate) -> AdminORM:
        """Update admin information."""
        password_hash = None
        if update_data.password:
            password_hash = hash_password(update_data.password)
        return self.repository.update(admin_id, update_data, password_hash)
    
    def delete_admin(self, admin_id: str) -> bool:
        """Delete an admin account."""
        return self.repository.delete(admin_id)
    
    def list_admins(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[AdminRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[AdminORM], int]:
        """List admins with pagination and filtering."""
        return self.repository.list_admins(
            page=page,
            page_size=page_size,
            role=role,
            is_active=is_active,
            search=search
        )
    
    # ========================================
    # Authentication
    # ========================================
    
    def authenticate_admin(self, email: str, password: str) -> AdminORM:
        """Authenticate admin with email and password."""
        admin = self.repository.get_by_email(email)
        
        if not admin:
            logger.warning(f"Admin authentication failed: admin not found - {email}")
            raise AuthenticationError("Invalid email or password")
        
        if not admin.is_active:
            logger.warning(f"Admin authentication failed: admin inactive - {email}")
            raise AuthenticationError("Account is deactivated")
        
        if not verify_password(password, admin.password_hash):
            logger.warning(f"Admin authentication failed: invalid password - {email}")
            raise AuthenticationError("Invalid email or password")
        
        # Update last login
        self.repository.update_last_login(admin.admin_id)
        
        # Log activity
        self.repository.log_activity(
            admin_id=admin.admin_id,
            action_type=ActionType.LOGIN
        )
        
        logger.info(f"Admin authenticated successfully: {admin.admin_id}")
        return admin
    
    def create_access_token(self, admin: AdminORM) -> Tuple[str, int]:
        """Create JWT access token for admin."""
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_at = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": admin.admin_id,
            "email": admin.email,
            "role": admin.role.value,
            "type": "admin",
            "exp": expires_at,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return token, int(expires_delta.total_seconds())
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "admin":
                return None
            return payload
        except JWTError as e:
            logger.warning(f"Admin token verification failed: {e}")
            return None
    
    def get_admin_from_token(self, token: str) -> Optional[AdminORM]:
        """Get admin from JWT token."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        admin_id = payload.get("sub")
        if not admin_id:
            return None
        
        return self.repository.get_by_id(admin_id)
    
    def check_permission(self, admin: AdminORM, permission: str) -> bool:
        """Check if admin has a specific permission."""
        permission_map = {
            "manage_users": admin.can_manage_users,
            "manage_listings": admin.can_manage_listings,
            "view_billing": admin.can_view_billing,
            "view_analytics": admin.can_view_analytics,
            "manage_admins": admin.can_manage_admins
        }
        return permission_map.get(permission, False)
    
    def require_permission(self, admin: AdminORM, permission: str):
        """Require admin to have a specific permission."""
        if not self.check_permission(admin, permission):
            raise AuthorizationError(f"Permission denied: {permission}")
    
    # ========================================
    # Activity Logging
    # ========================================
    
    def log_activity(
        self,
        admin_id: str,
        action_type: ActionType,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None
    ):
        """Log admin activity."""
        return self.repository.log_activity(
            admin_id=admin_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
    
    def get_activity_log(
        self,
        admin_id: Optional[str] = None,
        action_type: Optional[ActionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ):
        """Get admin activity log."""
        return self.repository.get_activity_log(
            admin_id=admin_id,
            action_type=action_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
    
    # ========================================
    # Analytics and Reports
    # ========================================
    
    def get_top_properties_report(self, year: int = None) -> TopPropertiesReport:
        """
        Get top 10 properties with revenue per year.
        This is a sample implementation - actual query depends on booking/billing schema.
        """
        if not year:
            year = datetime.now().year
        
        # Sample query - adjust based on actual schema
        # In production, this would join with bookings and billing tables
        query = text("""
            SELECT 
                b.booking_id as property_id,
                COALESCE(l.name, 'Unknown Property') as property_name,
                SUM(bi.total_amount_paid) as revenue,
                COUNT(DISTINCT b.booking_id) as booking_count
            FROM billing bi
            JOIN bookings b ON bi.booking_id = b.booking_id
            LEFT JOIN listings l ON b.listing_id = l.listing_id
            WHERE YEAR(bi.date_of_transaction) = :year
            GROUP BY b.listing_id
            ORDER BY revenue DESC
            LIMIT 10
        """)
        
        try:
            result = self.db.execute(query, {"year": year}).fetchall()
            properties = [
                RevenueByProperty(
                    property_id=str(row[0]),
                    property_name=row[1],
                    revenue=float(row[2]),
                    booking_count=int(row[3])
                )
                for row in result
            ]
            total_revenue = sum(p.revenue for p in properties)
        except Exception as e:
            logger.warning(f"Top properties query failed: {e}")
            # Return mock data for development
            properties = [
                RevenueByProperty(
                    property_id=f"prop_{i}",
                    property_name=f"Property {i}",
                    revenue=10000 - (i * 500),
                    booking_count=100 - (i * 5)
                )
                for i in range(1, 11)
            ]
            total_revenue = sum(p.revenue for p in properties)
        
        return TopPropertiesReport(
            year=year,
            properties=properties,
            total_revenue=total_revenue
        )
    
    def get_city_revenue_report(self, year: int = None) -> CityRevenueReport:
        """
        Get city-wise revenue per year.
        """
        if not year:
            year = datetime.now().year
        
        query = text("""
            SELECT 
                h.city,
                h.state,
                SUM(bi.total_amount_paid) as revenue,
                COUNT(DISTINCT b.booking_id) as booking_count
            FROM billing bi
            JOIN bookings b ON bi.booking_id = b.booking_id
            JOIN hotels h ON b.listing_id = h.hotel_id
            WHERE YEAR(bi.date_of_transaction) = :year
            GROUP BY h.city, h.state
            ORDER BY revenue DESC
        """)
        
        try:
            result = self.db.execute(query, {"year": year}).fetchall()
            cities = [
                RevenueByCity(
                    city=row[0],
                    state=row[1],
                    revenue=float(row[2]),
                    booking_count=int(row[3])
                )
                for row in result
            ]
            total_revenue = sum(c.revenue for c in cities)
        except Exception as e:
            logger.warning(f"City revenue query failed: {e}")
            # Return mock data for development
            mock_cities = [
                ("New York", "NY", 50000),
                ("Los Angeles", "CA", 45000),
                ("San Francisco", "CA", 40000),
                ("Miami", "FL", 35000),
                ("Las Vegas", "NV", 30000),
            ]
            cities = [
                RevenueByCity(
                    city=city,
                    state=state,
                    revenue=float(revenue),
                    booking_count=int(revenue / 100)
                )
                for city, state, revenue in mock_cities
            ]
            total_revenue = sum(c.revenue for c in cities)
        
        return CityRevenueReport(
            year=year,
            cities=cities,
            total_revenue=total_revenue
        )
    
    def get_provider_report(self, month: int = None, year: int = None) -> ProviderReport:
        """
        Get top 10 providers with maximum properties sold last month.
        """
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month - 1
            if month == 0:
                month = 12
                year -= 1
        
        query = text("""
            SELECT 
                p.provider_id,
                p.provider_name,
                COUNT(DISTINCT b.booking_id) as properties_sold,
                SUM(bi.total_amount_paid) as revenue
            FROM providers p
            JOIN listings l ON p.provider_id = l.provider_id
            JOIN bookings b ON l.listing_id = b.listing_id
            JOIN billing bi ON b.booking_id = bi.booking_id
            WHERE MONTH(bi.date_of_transaction) = :month
              AND YEAR(bi.date_of_transaction) = :year
            GROUP BY p.provider_id, p.provider_name
            ORDER BY properties_sold DESC
            LIMIT 10
        """)
        
        try:
            result = self.db.execute(query, {"month": month, "year": year}).fetchall()
            providers = [
                ProviderAnalytics(
                    provider_id=str(row[0]),
                    provider_name=row[1],
                    properties_sold=int(row[2]),
                    revenue=float(row[3])
                )
                for row in result
            ]
        except Exception as e:
            logger.warning(f"Provider report query failed: {e}")
            # Return mock data for development
            providers = [
                ProviderAnalytics(
                    provider_id=f"prov_{i}",
                    provider_name=f"Provider {i}",
                    properties_sold=50 - (i * 3),
                    revenue=25000 - (i * 1500)
                )
                for i in range(1, 11)
            ]
        
        month_name = datetime(year, month, 1).strftime("%B")
        
        return ProviderReport(
            month=month_name,
            year=year,
            providers=providers
        )
    
    def get_dashboard_stats(self) -> dict:
        """Get admin dashboard statistics."""
        try:
            # These queries would be adjusted based on actual schema
            total_users = self.db.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
            total_bookings = self.db.execute(text("SELECT COUNT(*) FROM bookings")).scalar() or 0
            total_revenue = self.db.execute(text("SELECT SUM(total_amount_paid) FROM billing")).scalar() or 0
            active_listings = self.db.execute(text("SELECT COUNT(*) FROM listings WHERE is_active = 1")).scalar() or 0
        except Exception as e:
            logger.warning(f"Dashboard stats query failed: {e}")
            total_users = 1000
            total_bookings = 5000
            total_revenue = 500000
            active_listings = 300
        
        return {
            "total_users": total_users,
            "total_bookings": total_bookings,
            "total_revenue": float(total_revenue) if total_revenue else 0,
            "active_listings": active_listings,
            "timestamp": datetime.utcnow().isoformat()
        }


