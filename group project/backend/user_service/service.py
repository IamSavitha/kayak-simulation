"""
User Service - Business Logic Layer
Handles user operations, authentication, and business rules.
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import logging

from .models import UserORM, UserCreate, UserUpdate, UserResponse, UserLogin
from .repository import UserRepository, DuplicateUserError, UserNotFoundError
from shared.config import settings

logger = logging.getLogger(__name__)

# Password hashing - using sha256_crypt as fallback, bcrypt has 72-byte limit issue in v5.0
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


class UserService:
    """
    User Service - Business Logic Layer
    Handles user CRUD operations, authentication, and profile management.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)
    
    # ========================================
    # User CRUD Operations
    # ========================================
    
    def create_user(self, user_data: UserCreate) -> UserORM:
        """
        Create a new user account.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            DuplicateUserError: If user already exists
        """
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user via repository
        user = self.repository.create(user_data, password_hash)
        
        logger.info(f"User created successfully: {user.user_id}")
        return user
    
    def get_user(self, user_id: str) -> Optional[UserORM]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID (SSN format)
            
        Returns:
            User or None if not found
        """
        return self.repository.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[UserORM]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None if not found
        """
        return self.repository.get_by_email(email)
    
    def update_user(
        self, 
        user_id: str, 
        update_data: UserUpdate
    ) -> UserORM:
        """
        Update user information.
        
        Args:
            user_id: User ID
            update_data: Fields to update
            
        Returns:
            Updated user
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        # Hash new password if provided
        password_hash = None
        if update_data.password:
            password_hash = pwd_context.hash(update_data.password)
        
        return self.repository.update(user_id, update_data, password_hash)
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        return self.repository.delete(user_id)
    
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
            page: Page number
            page_size: Items per page
            state: Filter by state
            city: Filter by city
            is_active: Filter by active status
            search: Search term
            
        Returns:
            Tuple of (users, total_count)
        """
        return self.repository.list_users(
            page=page,
            page_size=page_size,
            state=state,
            city=city,
            is_active=is_active,
            search=search
        )
    
    # ========================================
    # Authentication
    # ========================================
    
    def authenticate_user(self, email: str, password: str) -> UserORM:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Authenticated user
            
        Raises:
            AuthenticationError: If authentication fails
        """
        user = self.repository.get_by_email(email, use_cache=False)
        
        if not user:
            logger.warning(f"Authentication failed: user not found - {email}")
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {email}")
            raise AuthenticationError("Account is deactivated")
        
        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password - {email}")
            raise AuthenticationError("Invalid email or password")
        
        # Update last login
        self.repository.update_last_login(user.user_id)
        
        logger.info(f"User authenticated successfully: {user.user_id}")
        return user
    
    def create_access_token(self, user: UserORM) -> Tuple[str, int]:
        """
        Create JWT access token for user.
        
        Args:
            user: Authenticated user
            
        Returns:
            Tuple of (token, expires_in_seconds)
        """
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_at = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user.user_id,
            "email": user.email,
            "type": "user",
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
        """
        Verify JWT token and return payload.
        
        Args:
            token: JWT token
            
        Returns:
            Token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[UserORM]:
        """
        Get user from JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            User or None if token invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return self.repository.get_by_id(user_id)
    
    # ========================================
    # Profile Management
    # ========================================
    
    def update_profile_image(self, user_id: str, image_url: str) -> UserORM:
        """
        Update user's profile image.
        
        Args:
            user_id: User ID
            image_url: URL of uploaded image
            
        Returns:
            Updated user
        """
        update_data = UserUpdate(profile_image_url=image_url)
        return self.repository.update(user_id, update_data)
    
    def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user's password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            AuthenticationError: If current password is incorrect
            UserNotFoundError: If user doesn't exist
        """
        user = self.repository.get_by_id(user_id, use_cache=False)
        
        if not user:
            raise UserNotFoundError(user_id)
        
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        
        update_data = UserUpdate(password=new_password)
        new_hash = pwd_context.hash(new_password)
        self.repository.update(user_id, update_data, new_hash)
        
        logger.info(f"Password changed for user: {user_id}")
        return True
    
    def deactivate_user(self, user_id: str) -> UserORM:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        user = self.repository.get_by_id(user_id, use_cache=False)
        if not user:
            raise UserNotFoundError(user_id)
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        
        # Invalidate cache
        self.repository._invalidate_user_cache(user)
        
        logger.info(f"User deactivated: {user_id}")
        return user
    
    def reactivate_user(self, user_id: str) -> UserORM:
        """
        Reactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        user = self.repository.get_by_id(user_id, use_cache=False)
        if not user:
            raise UserNotFoundError(user_id)
        
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        
        # Invalidate cache
        self.repository._invalidate_user_cache(user)
        
        logger.info(f"User reactivated: {user_id}")
        return user
    
    # ========================================
    # Statistics
    # ========================================
    
    def get_user_stats(self) -> dict:
        """Get user statistics"""
        return {
            "total_users": self.repository.count_users(),
            "active_users": self.repository.count_active_users()
        }


