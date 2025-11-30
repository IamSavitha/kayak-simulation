"""
Custom exceptions - Team 5 compatible
"""
from fastapi import HTTPException, status

class ListingNotFoundException(HTTPException):
    def __init__(self, listing_type: str, listing_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{listing_type} with ID {listing_id} not found"
        )

class DuplicateListingException(HTTPException):
    def __init__(self, listing_type: str, listing_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{listing_type} with ID {listing_id} already exists"
        )

class AvailabilityException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

class ValidationException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )

class DatabaseException(HTTPException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

class KafkaException(Exception):
    """Exception for Kafka operations"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

