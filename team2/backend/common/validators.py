"""
Input validators - Team 5 compatible
"""
import re
from typing import Optional

# Valid US state abbreviations
VALID_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
]

def validate_state(state: str) -> bool:
    """Validate US state abbreviation"""
    return state.upper() in VALID_STATES

def validate_zip_code(zip_code: str) -> bool:
    """Validate ZIP code format (##### or #####-####)"""
    pattern = r'^\d{5}(-\d{4})?$'
    return bool(re.match(pattern, zip_code))

def validate_ssn(ssn: str) -> bool:
    """Validate SSN format (###-##-####)"""
    pattern = r'^\d{3}-\d{2}-\d{4}$'
    return bool(re.match(pattern, ssn))

def validate_airport_code(code: str) -> bool:
    """Validate airport code (3 letters)"""
    pattern = r'^[A-Z]{3}$'
    return bool(re.match(pattern, code.upper()))

def validate_price(price: float) -> bool:
    """Validate price is positive"""
    return price > 0

def validate_rating(rating: float) -> bool:
    """Validate rating is between 0 and 5"""
    return 0 <= rating <= 5

def sanitize_string(value: Optional[str]) -> Optional[str]:
    """Sanitize string input"""
    if value is None:
        return None
    return value.strip()

