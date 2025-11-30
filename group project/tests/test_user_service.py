"""
Unit tests for User Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.user_service.models import UserCreate, UserUpdate, UserORM, CreditCardInfo
from backend.user_service.repository import UserRepository, DuplicateUserError, UserNotFoundError
from backend.user_service.service import UserService, AuthenticationError


class TestUserModels:
    """Tests for User Pydantic models"""
    
    def test_user_create_valid(self):
        """Test valid user creation model"""
        user = UserCreate(
            user_id="123-45-6789",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="5551234567",
            address="123 Main Street",
            city="San Jose",
            state="CA",
            zip_code="95112",
            password="securepass123"
        )
        assert user.user_id == "123-45-6789"
        assert user.state == "CA"
    
    def test_user_create_invalid_ssn(self):
        """Test user creation with invalid SSN"""
        with pytest.raises(ValueError):
            UserCreate(
                user_id="invalid-ssn",
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone_number="5551234567",
                address="123 Main Street",
                city="San Jose",
                state="CA",
                zip_code="95112",
                password="securepass123"
            )
    
    def test_user_create_invalid_zip(self):
        """Test user creation with invalid ZIP"""
        with pytest.raises(ValueError):
            UserCreate(
                user_id="123-45-6789",
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone_number="5551234567",
                address="123 Main Street",
                city="San Jose",
                state="CA",
                zip_code="1234",  # Invalid
                password="securepass123"
            )
    
    def test_user_create_invalid_state(self):
        """Test user creation with invalid state"""
        with pytest.raises(ValueError):
            UserCreate(
                user_id="123-45-6789",
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone_number="5551234567",
                address="123 Main Street",
                city="San Jose",
                state="XX",  # Invalid
                zip_code="95112",
                password="securepass123"
            )
    
    def test_user_update_partial(self):
        """Test partial user update model"""
        update = UserUpdate(first_name="Jane")
        assert update.first_name == "Jane"
        assert update.last_name is None
    
    def test_credit_card_info(self):
        """Test credit card info model"""
        cc = CreditCardInfo(
            card_number="4111111111111111",
            expiry_date="12/2025",
            card_type="VISA"
        )
        assert cc.card_number == "4111111111111111"


class TestUserRepository:
    """Tests for User Repository"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return MagicMock()
    
    @pytest.fixture
    def mock_cache(self):
        """Create mock cache"""
        with patch('backend.user_service.repository.UserCache') as mock:
            yield mock.return_value
    
    @pytest.fixture
    def repository(self, mock_db, mock_cache):
        """Create repository with mocks"""
        repo = UserRepository(mock_db)
        repo.cache = mock_cache
        return repo
    
    def test_create_user_success(self, repository, mock_db):
        """Test successful user creation"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        user_data = UserCreate(
            user_id="123-45-6789",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="5551234567",
            address="123 Main Street",
            city="San Jose",
            state="CA",
            zip_code="95112",
            password="securepass123"
        )
        
        result = repository.create(user_data, "hashed_password")
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_create_duplicate_user(self, repository, mock_db):
        """Test duplicate user creation raises error"""
        existing_user = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        user_data = UserCreate(
            user_id="123-45-6789",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="5551234567",
            address="123 Main Street",
            city="San Jose",
            state="CA",
            zip_code="95112",
            password="securepass123"
        )
        
        with pytest.raises(DuplicateUserError):
            repository.create(user_data, "hashed_password")
    
    def test_get_by_id_cache_hit(self, repository, mock_cache):
        """Test cache hit for get by ID"""
        mock_cache.get_user.return_value = {
            "user_id": "123-45-6789",
            "first_name": "John"
        }
        
        result = repository.get_by_id("123-45-6789")
        
        mock_cache.get_user.assert_called_with("123-45-6789")
    
    def test_get_by_id_cache_miss(self, repository, mock_db, mock_cache):
        """Test cache miss for get by ID"""
        mock_cache.get_user.return_value = None
        mock_user = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = repository.get_by_id("123-45-6789")
        
        mock_db.query.assert_called()
    
    def test_delete_user_not_found(self, repository, mock_db):
        """Test delete non-existent user"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(UserNotFoundError):
            repository.delete("999-99-9999")


class TestUserService:
    """Tests for User Service"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_db):
        """Create service with mock"""
        return UserService(mock_db)
    
    def test_authenticate_user_success(self, service, mock_db):
        """Test successful user authentication"""
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9Wy"  # "password"
        mock_user.user_id = "123-45-6789"
        
        service.repository.get_by_email = Mock(return_value=mock_user)
        
        with patch('backend.user_service.service.pwd_context') as mock_pwd:
            mock_pwd.verify.return_value = True
            
            result = service.authenticate_user("john@example.com", "password")
            
            assert result == mock_user
    
    def test_authenticate_user_invalid_password(self, service):
        """Test authentication with invalid password"""
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.password_hash = "hashed"
        
        service.repository.get_by_email = Mock(return_value=mock_user)
        
        with patch('backend.user_service.service.pwd_context') as mock_pwd:
            mock_pwd.verify.return_value = False
            
            with pytest.raises(AuthenticationError):
                service.authenticate_user("john@example.com", "wrongpassword")
    
    def test_authenticate_user_not_found(self, service):
        """Test authentication with non-existent user"""
        service.repository.get_by_email = Mock(return_value=None)
        
        with pytest.raises(AuthenticationError):
            service.authenticate_user("nobody@example.com", "password")
    
    def test_authenticate_inactive_user(self, service):
        """Test authentication with inactive user"""
        mock_user = Mock()
        mock_user.is_active = False
        
        service.repository.get_by_email = Mock(return_value=mock_user)
        
        with pytest.raises(AuthenticationError):
            service.authenticate_user("inactive@example.com", "password")
    
    def test_create_access_token(self, service):
        """Test JWT token creation"""
        mock_user = Mock()
        mock_user.user_id = "123-45-6789"
        mock_user.email = "john@example.com"
        
        token, expires_in = service.create_access_token(mock_user)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert expires_in > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


