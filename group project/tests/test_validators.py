"""
Unit tests for validation utilities
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.shared.validators import (
    validate_ssn, validate_user_id, validate_zip_code, validate_state,
    validate_email, validate_phone, validate_address, validate_credit_card,
    normalize_phone, mask_credit_card, mask_ssn,
    InvalidSSNError, InvalidUserIdError, InvalidZipCodeError, MalformedStateError,
    ValidationError, US_STATES
)


class TestSSNValidation:
    """Tests for SSN validation"""
    
    def test_valid_ssn_format(self):
        """Test valid SSN formats"""
        valid_ssns = [
            "123-45-6789",
            "000-00-0000",
            "999-99-9999",
            "111-22-3333",
        ]
        for ssn in valid_ssns:
            assert validate_ssn(ssn) is True
    
    def test_invalid_ssn_format(self):
        """Test invalid SSN formats"""
        invalid_ssns = [
            "1234-56-7890",  # Too many digits
            "12-345-6789",   # Wrong grouping
            "123-456-789",   # Wrong grouping
            "123456789",     # No dashes
            "123-45-678",    # Too few digits
            "12a-45-6789",   # Contains letters
            "",              # Empty
            None,            # None
        ]
        for ssn in invalid_ssns:
            with pytest.raises(InvalidSSNError):
                validate_ssn(ssn)
    
    def test_user_id_validation(self):
        """Test user ID validation (same as SSN)"""
        assert validate_user_id("123-45-6789") is True
        
        with pytest.raises(InvalidUserIdError):
            validate_user_id("invalid")


class TestZipCodeValidation:
    """Tests for ZIP code validation"""
    
    def test_valid_5_digit_zip(self):
        """Test valid 5-digit ZIP codes"""
        valid_zips = ["95123", "12345", "00000", "99999", "10293", "90086"]
        for zip_code in valid_zips:
            assert validate_zip_code(zip_code) is True
    
    def test_valid_9_digit_zip(self):
        """Test valid 9-digit ZIP codes"""
        valid_zips = ["95123-4567", "12345-6789", "90086-1929"]
        for zip_code in valid_zips:
            assert validate_zip_code(zip_code) is True
    
    def test_invalid_zip_codes(self):
        """Test invalid ZIP codes as per project requirements"""
        invalid_zips = [
            "1247",        # 4 digits
            "1829A",       # Contains letter
            "37849-392",   # 5-3 format instead of 5-4
            "2374-2384",   # 4-4 format
            "123456",      # 6 digits
            "",            # Empty
        ]
        for zip_code in invalid_zips:
            with pytest.raises(InvalidZipCodeError):
                validate_zip_code(zip_code)


class TestStateValidation:
    """Tests for state validation"""
    
    def test_valid_state_abbreviations(self):
        """Test valid state abbreviations"""
        for abbr in US_STATES.keys():
            result = validate_state(abbr)
            assert result == abbr
    
    def test_valid_state_full_names(self):
        """Test valid state full names"""
        test_cases = [
            ("California", "CA"),
            ("New York", "NY"),
            ("TEXAS", "TX"),
            ("florida", "FL"),
        ]
        for name, expected in test_cases:
            assert validate_state(name) == expected
    
    def test_invalid_states(self):
        """Test invalid state values"""
        invalid_states = [
            "XX",       # Invalid abbreviation
            "Cali",     # Invalid name
            "PR",       # Puerto Rico (territory)
            "",         # Empty
            None,       # None
        ]
        for state in invalid_states:
            with pytest.raises(MalformedStateError):
                validate_state(state)


class TestEmailValidation:
    """Tests for email validation"""
    
    def test_valid_emails(self):
        """Test valid email formats"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
        ]
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_invalid_emails(self):
        """Test invalid email formats"""
        invalid_emails = [
            "invalid",
            "missing@",
            "@nodomain.com",
            "",
        ]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                validate_email(email)


class TestPhoneValidation:
    """Tests for phone validation"""
    
    def test_valid_phones(self):
        """Test valid phone formats"""
        valid_phones = [
            "5551234567",
            "(555) 123-4567",
            "555-123-4567",
            "555.123.4567",
        ]
        for phone in valid_phones:
            assert validate_phone(phone) is True
    
    def test_invalid_phones(self):
        """Test invalid phone formats"""
        invalid_phones = [
            "123",           # Too short
            "12345678901",   # Too long
            "555-CALL-NOW",  # Contains letters
        ]
        for phone in invalid_phones:
            with pytest.raises(ValidationError):
                validate_phone(phone)
    
    def test_normalize_phone(self):
        """Test phone normalization"""
        assert normalize_phone("5551234567") == "(555) 123-4567"
        assert normalize_phone("555-123-4567") == "(555) 123-4567"


class TestAddressValidation:
    """Tests for address validation"""
    
    def test_valid_address(self):
        """Test valid address"""
        result = validate_address(
            address="123 Main Street",
            city="San Jose",
            state="CA",
            zip_code="95112"
        )
        assert result["state"] == "CA"
        assert result["city"] == "San Jose"
    
    def test_invalid_address_components(self):
        """Test invalid address components"""
        with pytest.raises(ValidationError):
            validate_address("Ab", "City", "CA", "95112")  # Address too short
        
        with pytest.raises(MalformedStateError):
            validate_address("123 Main St", "City", "XX", "95112")  # Invalid state


class TestCreditCardValidation:
    """Tests for credit card validation"""
    
    def test_valid_credit_cards(self):
        """Test valid credit card numbers (test numbers)"""
        valid_cards = [
            "4111111111111111",  # Visa test
            "5500000000000004",  # Mastercard test
        ]
        for card in valid_cards:
            assert validate_credit_card(card) is True
    
    def test_invalid_credit_cards(self):
        """Test invalid credit card numbers"""
        invalid_cards = [
            "1234567890123456",  # Fails Luhn
            "12345",             # Too short
            "123456789012345678901",  # Too long
            "411111111111111a",  # Contains letter
        ]
        for card in invalid_cards:
            with pytest.raises(ValidationError):
                validate_credit_card(card)


class TestMasking:
    """Tests for data masking functions"""
    
    def test_mask_credit_card(self):
        """Test credit card masking"""
        assert mask_credit_card("4111111111111111") == "****-****-****-1111"
    
    def test_mask_ssn(self):
        """Test SSN masking"""
        assert mask_ssn("123-45-6789") == "***-**-6789"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


