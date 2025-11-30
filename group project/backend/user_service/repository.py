"""
User Service - Repository Layer
Handles database operations for users with caching support.
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_
from datetime import datetime
import logging

from .models import UserORM, UserCreate, UserUpdate
from shared.cache import UserCache, get_cache_service
from shared.database import TransactionManager

logger = logging.getLogger(__name__)


class DuplicateUserError(Exception):
    """Raised when attempting to create a user that already exists"""
    def __init__(self, user_id: str = None, email: str = None):
        self.user_id = user_id
        self.email = email
        if user_id:
            super().__init__(f"User with ID {user_id} already exists")
        elif email:
            super().__init__(f"User with email {email} already exists")
        else:
            super().__init__("User already exists")


class UserNotFoundError(Exception):
    """Raised when user is not found"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class UserRepository:
    """
    Repository for User entity operations.
    Implements caching with Redis for performance optimization.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = UserCache()
        self.cache_ttl = 3600  # 1 hour
    
    def create(self, user_data: UserCreate, password_hash: str) -> UserORM:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            password_hash: Hashed password
            
        Returns:
            Created UserORM instance
            
        Raises:
            DuplicateUserError: If user ID or email already exists
        """
        # Check for existing user
        existing_by_id = self.db.query(UserORM).filter(
            UserORM.user_id == user_data.user_id
        ).first()
        if existing_by_id:
            raise DuplicateUserError(user_id=user_data.user_id)
        
        existing_by_email = self.db.query(UserORM).filter(
            UserORM.email == user_data.email
        ).first()
        if existing_by_email:
            raise DuplicateUserError(email=user_data.email)
        
        # Create user
        user = UserORM(
            user_id=user_data.user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            address=user_data.address,
            city=user_data.city,
            state=user_data.state,
            zip_code=user_data.zip_code,
            profile_image_url=user_data.profile_image_url,
            password_hash=password_hash,
        )
        
        # Add credit card info if provided
        if user_data.credit_card:
            user.credit_card_last_four = user_data.credit_card.card_number[-4:]
            user.credit_card_expiry = user_data.credit_card.expiry_date
            user.credit_card_type = user_data.credit_card.card_type
            user.billing_address = user_data.credit_card.billing_address
            user.billing_city = user_data.credit_card.billing_city
            user.billing_state = user_data.credit_card.billing_state
            user.billing_zip_code = user_data.credit_card.billing_zip_code
            # Note: In production, encrypt card_number before storing
            # user.credit_card_number_encrypted = encrypt(user_data.credit_card.card_number)
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Cache the new user
            self._cache_user(user)
            
            logger.info(f"Created user: {user.user_id}")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            if "email" in str(e.orig).lower():
                raise DuplicateUserError(email=user_data.email)
            raise DuplicateUserError(user_id=user_data.user_id)
    
    def get_by_id(self, user_id: str, use_cache: bool = True) -> Optional[UserORM]:
        """
        Get user by ID with caching.
        
        Args:
            user_id: User ID (SSN format)
            use_cache: Whether to use Redis cache
            
        Returns:
            UserORM instance or None
        """
        # Try cache first
        if use_cache:
            cached = self.cache.get_user(user_id)
            if cached:
                logger.debug(f"Cache hit for user: {user_id}")
                # Return cached data as ORM-like object
                return self._dict_to_user_orm(cached)
        
        # Query database
        user = self.db.query(UserORM).filter(UserORM.user_id == user_id).first()
        
        if user and use_cache:
            self._cache_user(user)
        
        return user
    
    def get_by_email(self, email: str, use_cache: bool = True) -> Optional[UserORM]:
        """
        Get user by email with caching.
        
        Args:
            email: User email
            use_cache: Whether to use Redis cache
            
        Returns:
            UserORM instance or None
        """
        # Try cache first
        if use_cache:
            cached = self.cache.get_user_by_email(email)
            if cached:
                logger.debug(f"Cache hit for user email: {email}")
                return self._dict_to_user_orm(cached)
        
        # Query database
        user = self.db.query(UserORM).filter(UserORM.email == email).first()
        
        if user and use_cache:
            self._cache_user(user)
            self.cache.set_user_by_email(email, user.to_dict(mask_sensitive=False))
        
        return user
    
    def update(self, user_id: str, update_data: UserUpdate, password_hash: Optional[str] = None) -> UserORM:
        """
        Update user information.
        
        Args:
            user_id: User ID
            update_data: Update data
            password_hash: New password hash (if password change)
            
        Returns:
            Updated UserORM instance
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = self.db.query(UserORM).filter(UserORM.user_id == user_id).first()
        
        if not user:
            raise UserNotFoundError(user_id)
        
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
        
        for field, value in update_dict.items():
            if field == 'credit_card':
                # Handle credit card update
                cc = update_data.credit_card
                user.credit_card_last_four = cc.card_number[-4:]
                user.credit_card_expiry = cc.expiry_date
                user.credit_card_type = cc.card_type
                user.billing_address = cc.billing_address
                user.billing_city = cc.billing_city
                user.billing_state = cc.billing_state
                user.billing_zip_code = cc.billing_zip_code
            elif field != 'password':
                setattr(user, field, value)
        
        if password_hash:
            user.password_hash = password_hash
        
        try:
            self.db.commit()
            self.db.refresh(user)
            
            # Invalidate and update cache
            self._invalidate_user_cache(user)
            self._cache_user(user)
            
            logger.info(f"Updated user: {user_id}")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            if "email" in str(e.orig).lower():
                raise DuplicateUserError(email=update_data.email)
            raise
    
    def delete(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = self.db.query(UserORM).filter(UserORM.user_id == user_id).first()
        
        if not user:
            raise UserNotFoundError(user_id)
        
        email = user.email
        
        self.db.delete(user)
        self.db.commit()
        
        # Invalidate cache
        self.cache.invalidate_user(user_id)
        self.cache.invalidate_user_by_email(email)
        
        logger.info(f"Deleted user: {user_id}")
        return True
    
    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        state: Optional[str] = None,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[UserORM], int]:
        """
        List users with pagination and filtering.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            state: Filter by state
            city: Filter by city
            is_active: Filter by active status
            search: Search in name and email
            
        Returns:
            Tuple of (users list, total count)
        """
        query = self.db.query(UserORM)
        
        # Apply filters
        if state:
            query = query.filter(UserORM.state == state.upper())
        
        if city:
            query = query.filter(UserORM.city.ilike(f"%{city}%"))
        
        if is_active is not None:
            query = query.filter(UserORM.is_active == is_active)
        
        if search:
            search_filter = or_(
                UserORM.first_name.ilike(f"%{search}%"),
                UserORM.last_name.ilike(f"%{search}%"),
                UserORM.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        users = query.order_by(UserORM.created_at.desc()).offset(offset).limit(page_size).all()
        
        return users, total
    
    def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp"""
        self.db.query(UserORM).filter(
            UserORM.user_id == user_id
        ).update({"last_login_at": datetime.utcnow()})
        self.db.commit()
        
        # Invalidate cache
        self.cache.invalidate_user(user_id)
    
    def _cache_user(self, user: UserORM) -> None:
        """Cache user data"""
        user_dict = user.to_dict(mask_sensitive=False)
        self.cache.set_user(user.user_id, user_dict, self.cache_ttl)
    
    def _invalidate_user_cache(self, user: UserORM) -> None:
        """Invalidate user cache entries"""
        self.cache.invalidate_user(user.user_id)
        self.cache.invalidate_user_by_email(user.email)
    
    def _dict_to_user_orm(self, data: dict) -> UserORM:
        """Convert cached dictionary back to UserORM-like object"""
        user = UserORM()
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user
    
    def count_users(self) -> int:
        """Get total user count"""
        return self.db.query(UserORM).count()
    
    def count_active_users(self) -> int:
        """Get active user count"""
        return self.db.query(UserORM).filter(UserORM.is_active == True).count()


