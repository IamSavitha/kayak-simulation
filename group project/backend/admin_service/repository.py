"""
Admin Service - Repository Layer
Handles database operations for administrators.
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_, desc
from datetime import datetime
import uuid
import logging

from .models import (
    AdminORM, AdminSessionORM, AdminActivityLogORM,
    AdminCreate, AdminUpdate, AdminRole, ActionType
)
from shared.cache import AdminCache, get_cache_service

logger = logging.getLogger(__name__)


class DuplicateAdminError(Exception):
    """Raised when attempting to create an admin that already exists"""
    def __init__(self, email: str = None):
        self.email = email
        super().__init__(f"Admin with email {email} already exists")


class AdminNotFoundError(Exception):
    """Raised when admin is not found"""
    def __init__(self, admin_id: str):
        self.admin_id = admin_id
        super().__init__(f"Admin with ID {admin_id} not found")


class AdminRepository:
    """
    Repository for Admin entity operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = AdminCache()
        self.cache_ttl = 3600  # 1 hour
    
    def create(self, admin_data: AdminCreate, password_hash: str, created_by: Optional[str] = None) -> AdminORM:
        """
        Create a new admin.
        
        Args:
            admin_data: Admin creation data
            password_hash: Hashed password
            created_by: ID of admin creating this account
            
        Returns:
            Created AdminORM instance
            
        Raises:
            DuplicateAdminError: If email already exists
        """
        # Check for existing admin with same email
        existing = self.db.query(AdminORM).filter(AdminORM.email == admin_data.email).first()
        if existing:
            raise DuplicateAdminError(email=admin_data.email)
        
        # Generate UUID for admin
        admin_id = str(uuid.uuid4())
        
        # Create admin
        admin = AdminORM(
            admin_id=admin_id,
            first_name=admin_data.first_name,
            last_name=admin_data.last_name,
            email=admin_data.email,
            phone_number=admin_data.phone_number,
            address=admin_data.address,
            city=admin_data.city,
            state=admin_data.state,
            zip_code=admin_data.zip_code,
            password_hash=password_hash,
            role=admin_data.role,
            access_level=admin_data.access_level,
            created_by=created_by
        )
        
        # Set permissions if provided
        if admin_data.permissions:
            admin.can_manage_users = admin_data.permissions.can_manage_users
            admin.can_manage_listings = admin_data.permissions.can_manage_listings
            admin.can_view_billing = admin_data.permissions.can_view_billing
            admin.can_view_analytics = admin_data.permissions.can_view_analytics
            admin.can_manage_admins = admin_data.permissions.can_manage_admins
        
        try:
            self.db.add(admin)
            self.db.commit()
            self.db.refresh(admin)
            
            # Cache the new admin
            self._cache_admin(admin)
            
            logger.info(f"Created admin: {admin.admin_id}")
            return admin
            
        except IntegrityError as e:
            self.db.rollback()
            raise DuplicateAdminError(email=admin_data.email)
    
    def get_by_id(self, admin_id: str, use_cache: bool = True) -> Optional[AdminORM]:
        """Get admin by ID with caching."""
        # Try cache first
        if use_cache:
            cached = self.cache.get_admin(admin_id)
            if cached:
                logger.debug(f"Cache hit for admin: {admin_id}")
                return self._dict_to_admin_orm(cached)
        
        # Query database
        admin = self.db.query(AdminORM).filter(AdminORM.admin_id == admin_id).first()
        
        if admin and use_cache:
            self._cache_admin(admin)
        
        return admin
    
    def get_by_email(self, email: str, use_cache: bool = False) -> Optional[AdminORM]:
        """Get admin by email."""
        return self.db.query(AdminORM).filter(AdminORM.email == email).first()
    
    def update(self, admin_id: str, update_data: AdminUpdate, password_hash: Optional[str] = None) -> AdminORM:
        """Update admin information."""
        admin = self.db.query(AdminORM).filter(AdminORM.admin_id == admin_id).first()
        
        if not admin:
            raise AdminNotFoundError(admin_id)
        
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
        
        for field, value in update_dict.items():
            if field == 'permissions':
                # Handle permissions update
                perms = update_data.permissions
                admin.can_manage_users = perms.can_manage_users
                admin.can_manage_listings = perms.can_manage_listings
                admin.can_view_billing = perms.can_view_billing
                admin.can_view_analytics = perms.can_view_analytics
                admin.can_manage_admins = perms.can_manage_admins
            elif field != 'password':
                setattr(admin, field, value)
        
        if password_hash:
            admin.password_hash = password_hash
        
        try:
            self.db.commit()
            self.db.refresh(admin)
            
            # Invalidate and update cache
            self.cache.invalidate_admin(admin_id)
            self._cache_admin(admin)
            
            logger.info(f"Updated admin: {admin_id}")
            return admin
            
        except IntegrityError as e:
            self.db.rollback()
            if "email" in str(e.orig).lower():
                raise DuplicateAdminError(email=update_data.email)
            raise
    
    def delete(self, admin_id: str) -> bool:
        """Delete an admin."""
        admin = self.db.query(AdminORM).filter(AdminORM.admin_id == admin_id).first()
        
        if not admin:
            raise AdminNotFoundError(admin_id)
        
        # Prevent deleting the last super admin
        if admin.role == AdminRole.SUPER_ADMIN:
            super_admin_count = self.db.query(AdminORM).filter(
                AdminORM.role == AdminRole.SUPER_ADMIN,
                AdminORM.is_active == True
            ).count()
            if super_admin_count <= 1:
                raise ValueError("Cannot delete the last super admin")
        
        self.db.delete(admin)
        self.db.commit()
        
        # Invalidate cache
        self.cache.invalidate_admin(admin_id)
        
        logger.info(f"Deleted admin: {admin_id}")
        return True
    
    def list_admins(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[AdminRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[AdminORM], int]:
        """List admins with pagination and filtering."""
        query = self.db.query(AdminORM)
        
        if role:
            query = query.filter(AdminORM.role == role)
        
        if is_active is not None:
            query = query.filter(AdminORM.is_active == is_active)
        
        if search:
            search_filter = or_(
                AdminORM.first_name.ilike(f"%{search}%"),
                AdminORM.last_name.ilike(f"%{search}%"),
                AdminORM.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        offset = (page - 1) * page_size
        admins = query.order_by(AdminORM.created_at.desc()).offset(offset).limit(page_size).all()
        
        return admins, total
    
    def update_last_login(self, admin_id: str) -> None:
        """Update admin's last login timestamp."""
        self.db.query(AdminORM).filter(
            AdminORM.admin_id == admin_id
        ).update({"last_login_at": datetime.utcnow()})
        self.db.commit()
        
        # Invalidate cache
        self.cache.invalidate_admin(admin_id)
    
    def log_activity(
        self,
        admin_id: str,
        action_type: ActionType,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None
    ) -> AdminActivityLogORM:
        """Log admin activity."""
        log_entry = AdminActivityLogORM(
            admin_id=admin_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    def get_activity_log(
        self,
        admin_id: Optional[str] = None,
        action_type: Optional[ActionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[AdminActivityLogORM], int]:
        """Get admin activity log with filtering."""
        query = self.db.query(AdminActivityLogORM)
        
        if admin_id:
            query = query.filter(AdminActivityLogORM.admin_id == admin_id)
        
        if action_type:
            query = query.filter(AdminActivityLogORM.action_type == action_type)
        
        if start_date:
            query = query.filter(AdminActivityLogORM.created_at >= start_date)
        
        if end_date:
            query = query.filter(AdminActivityLogORM.created_at <= end_date)
        
        total = query.count()
        offset = (page - 1) * page_size
        logs = query.order_by(desc(AdminActivityLogORM.created_at)).offset(offset).limit(page_size).all()
        
        return logs, total
    
    def _cache_admin(self, admin: AdminORM) -> None:
        """Cache admin data."""
        admin_dict = admin.to_dict()
        self.cache.set_admin(admin.admin_id, admin_dict, self.cache_ttl)
    
    def _dict_to_admin_orm(self, data: dict) -> AdminORM:
        """Convert cached dictionary back to AdminORM-like object."""
        admin = AdminORM()
        for key, value in data.items():
            if key == 'permissions':
                admin.can_manage_users = value.get('can_manage_users', True)
                admin.can_manage_listings = value.get('can_manage_listings', True)
                admin.can_view_billing = value.get('can_view_billing', True)
                admin.can_view_analytics = value.get('can_view_analytics', True)
                admin.can_manage_admins = value.get('can_manage_admins', False)
            elif key == 'role':
                admin.role = AdminRole(value) if value else None
            elif hasattr(admin, key):
                setattr(admin, key, value)
        return admin


