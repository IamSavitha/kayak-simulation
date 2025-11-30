"""
Validation utilities for Kayak Simulation
Implements SSN, ZIP code, and State validation as per project requirements.
"""

import re
from typing import Optional
from enum import Enum


class ValidationError(Exception):
    """Base validation error"""
    pass


class InvalidSSNError(ValidationError):
    """Raised when SSN format is invalid"""
    def __init__(self, ssn: str):
        self.ssn = ssn
        super().__init__(f"Invalid SSN format: {ssn}. Expected format: ###-##-####")


class MalformedStateError(ValidationError):
    """Raised when state abbreviation is invalid"""
    def __init__(self, state: str):
        self.state = state
        super().__init__(f"Malformed state: {state}. Must be a valid US state abbreviation or full name.")


class InvalidZipCodeError(ValidationError):
    """Raised when ZIP code format is invalid"""
    def __init__(self, zip_code: str):
        self.zip_code = zip_code
        super().__init__(f"Invalid ZIP code format: {zip_code}. Expected format: ##### or #####-####")


class InvalidUserIdError(ValidationError):
    """Raised when User ID (SSN) format is invalid"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"Invalid user ID format: {user_id}. Expected SSN format: ###-##-####")


# Valid US State abbreviations
US_STATES = {
    # Abbreviations
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}

# Reverse mapping: full name to abbreviation
STATE_NAME_TO_ABBR = {v.upper(): k for k, v in US_STATES.items()}


# SSN pattern: ###-##-####
SSN_PATTERN = re.compile(r'^[0-9]{3}-[0-9]{2}-[0-9]{4}$')

# ZIP code patterns: ##### or #####-####
ZIP_PATTERN_5 = re.compile(r'^[0-9]{5}$')
ZIP_PATTERN_9 = re.compile(r'^[0-9]{5}-[0-9]{4}$')


def validate_ssn(ssn: str) -> bool:
    """
    Validate SSN format according to project requirements.
    
    Pattern: [0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]
    
    Args:
        ssn: The Social Security Number to validate
        
    Returns:
        True if valid
        
    Raises:
        InvalidSSNError: If SSN format is invalid
    """
    if not ssn or not SSN_PATTERN.match(ssn):
        raise InvalidSSNError(ssn)
    return True


def validate_user_id(user_id: str) -> bool:
    """
    Validate User ID format (same as SSN format).
    
    Args:
        user_id: The User ID to validate
        
    Returns:
        True if valid
        
    Raises:
        InvalidUserIdError: If User ID format is invalid
    """
    if not user_id or not SSN_PATTERN.match(user_id):
        raise InvalidUserIdError(user_id)
    return True


def validate_zip_code(zip_code: str) -> bool:
    """
    Validate ZIP code format according to project requirements.
    
    Valid patterns:
    - #####
    - #####-####
    
    Examples of valid ZIP codes: 95123, 95192, 90086-1929
    Examples of invalid ZIP codes: 1247, 1829A, 37849-392, 2374-2384
    
    Args:
        zip_code: The ZIP code to validate
        
    Returns:
        True if valid
        
    Raises:
        InvalidZipCodeError: If ZIP code format is invalid
    """
    if not zip_code:
        raise InvalidZipCodeError(zip_code if zip_code else "empty")
    
    # Check if matches 5-digit or 9-digit format
    if ZIP_PATTERN_5.match(zip_code) or ZIP_PATTERN_9.match(zip_code):
        return True
    
    raise InvalidZipCodeError(zip_code)


def validate_state(state: str) -> str:
    """
    Validate state parameter - accepts US state abbreviations or full names.
    
    Args:
        state: State abbreviation (e.g., "CA") or full name (e.g., "California")
        
    Returns:
        The standardized state abbreviation (e.g., "CA")
        
    Raises:
        MalformedStateError: If state is not a valid US state
    """
    if not state:
        raise MalformedStateError(state if state else "empty")
    
    state_upper = state.upper().strip()
    
    # Check if it's a valid abbreviation
    if state_upper in US_STATES:
        return state_upper
    
    # Check if it's a valid full state name
    if state_upper in STATE_NAME_TO_ABBR:
        return STATE_NAME_TO_ABBR[state_upper]
    
    raise MalformedStateError(state)


def validate_email(email: str) -> bool:
    """
    Basic email format validation.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if valid format
        
    Raises:
        ValidationError: If email format is invalid
    """
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email or not email_pattern.match(email):
        raise ValidationError(f"Invalid email format: {email}")
    return True


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    Accepts formats: (###) ###-####, ###-###-####, ##########
    
    Args:
        phone: The phone number to validate
        
    Returns:
        True if valid format
        
    Raises:
        ValidationError: If phone format is invalid
    """
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Should be 10 digits for US phone numbers
    if not cleaned.isdigit() or len(cleaned) != 10:
        raise ValidationError(f"Invalid phone number format: {phone}. Expected 10-digit US phone number.")
    return True


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to standard format: (###) ###-####
    
    Args:
        phone: The phone number to normalize
        
    Returns:
        Normalized phone number string
    """
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    if len(cleaned) == 10 and cleaned.isdigit():
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    return phone


def validate_address(address: str, city: str, state: str, zip_code: str) -> dict:
    """
    Validate a complete address.
    
    Args:
        address: Street address
        city: City name
        state: State abbreviation or full name
        zip_code: ZIP code
        
    Returns:
        Dictionary with normalized address components
        
    Raises:
        ValidationError: If any component is invalid
    """
    if not address or len(address.strip()) < 5:
        raise ValidationError("Address is too short or empty")
    
    if not city or len(city.strip()) < 2:
        raise ValidationError("City name is too short or empty")
    
    # Validate and normalize state
    normalized_state = validate_state(state)
    
    # Validate ZIP code
    validate_zip_code(zip_code)
    
    return {
        "address": address.strip(),
        "city": city.strip().title(),
        "state": normalized_state,
        "zip_code": zip_code.strip()
    }


def validate_credit_card(card_number: str) -> bool:
    """
    Basic credit card number validation using Luhn algorithm.
    
    Args:
        card_number: Credit card number (can contain spaces or dashes)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If card number is invalid
    """
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', card_number)
    
    if not cleaned.isdigit():
        raise ValidationError("Credit card number must contain only digits")
    
    if len(cleaned) < 13 or len(cleaned) > 19:
        raise ValidationError("Credit card number must be between 13 and 19 digits")
    
    # Luhn algorithm
    def luhn_checksum(card_num: str) -> bool:
        def digits_of(n: str):
            return [int(d) for d in n]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        
        return checksum % 10 == 0
    
    if not luhn_checksum(cleaned):
        raise ValidationError("Invalid credit card number (failed checksum)")
    
    return True


def mask_credit_card(card_number: str) -> str:
    """
    Mask credit card number, showing only last 4 digits.
    
    Args:
        card_number: Credit card number
        
    Returns:
        Masked card number (e.g., "****-****-****-1234")
    """
    cleaned = re.sub(r'[\s\-]', '', card_number)
    if len(cleaned) >= 4:
        return f"****-****-****-{cleaned[-4:]}"
    return "****-****-****-****"


def mask_ssn(ssn: str) -> str:
    """
    Mask SSN, showing only last 4 digits.
    
    Args:
        ssn: Social Security Number
        
    Returns:
        Masked SSN (e.g., "***-**-1234")
    """
    if len(ssn) >= 4:
        return f"***-**-{ssn[-4:]}"
    return "***-**-****"


