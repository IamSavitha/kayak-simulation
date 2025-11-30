"""
Mock Data for Team 3 (Booking) and Team 4 (Billing) Services

Use these mocks until integration with actual services is complete.
Replace mock functions with real API calls when Team 3/4 provide their endpoints.

Team 3 - Booking Service (Barathi): Expected on port 8005 (TBD)
Team 4 - Billing Service (Daniel): Expected on port 8005
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
import random
import uuid


# ==================== Enums ====================

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingType(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    CAR = "car"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


# ==================== Mock Data ====================

# Sample booking data
MOCK_BOOKINGS: List[Dict[str, Any]] = [
    {
        "booking_id": "BK-001",
        "user_id": "123-45-6789",
        "booking_type": "flight",
        "listing_id": "FLT-ABC123",
        "listing_name": "San Francisco → New York",
        "provider": "United Airlines",
        "check_in_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "check_out_date": None,
        "num_passengers": 2,
        "num_rooms": None,
        "num_nights": None,
        "status": "confirmed",
        "total_price": 598.00,
        "booking_date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "booking_id": "BK-002",
        "user_id": "123-45-6789",
        "booking_type": "hotel",
        "listing_id": "HTL-XYZ789",
        "listing_name": "Marriott Times Square",
        "provider": "Marriott International",
        "check_in_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "check_out_date": (datetime.now() + timedelta(days=33)).isoformat(),
        "num_passengers": None,
        "num_rooms": 1,
        "num_nights": 3,
        "status": "confirmed",
        "total_price": 567.00,
        "booking_date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "booking_id": "BK-003",
        "user_id": "234-56-7890",
        "booking_type": "car",
        "listing_id": "CAR-DEF456",
        "listing_name": "Toyota RAV4 2023",
        "provider": "Hertz",
        "check_in_date": (datetime.now() + timedelta(days=15)).isoformat(),
        "check_out_date": (datetime.now() + timedelta(days=18)).isoformat(),
        "num_passengers": None,
        "num_rooms": None,
        "num_nights": None,
        "status": "pending",
        "total_price": 267.00,
        "booking_date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "booking_id": "BK-004",
        "user_id": "123-45-6789",
        "booking_type": "flight",
        "listing_id": "FLT-GHI321",
        "listing_name": "Los Angeles → Miami",
        "provider": "Delta Airlines",
        "check_in_date": (datetime.now() - timedelta(days=10)).isoformat(),
        "check_out_date": None,
        "num_passengers": 1,
        "num_rooms": None,
        "num_nights": None,
        "status": "completed",
        "total_price": 349.00,
        "booking_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=10)).isoformat(),
    },
    {
        "booking_id": "BK-005",
        "user_id": "345-67-8901",
        "booking_type": "hotel",
        "listing_id": "HTL-JKL654",
        "listing_name": "Hilton Downtown LA",
        "provider": "Hilton Hotels",
        "check_in_date": (datetime.now() - timedelta(days=5)).isoformat(),
        "check_out_date": (datetime.now() - timedelta(days=2)).isoformat(),
        "num_passengers": None,
        "num_rooms": 2,
        "num_nights": 3,
        "status": "completed",
        "total_price": 687.00,
        "booking_date": (datetime.now() - timedelta(days=20)).isoformat(),
        "created_at": (datetime.now() - timedelta(days=20)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=2)).isoformat(),
    },
]

# Sample billing data
MOCK_BILLINGS: List[Dict[str, Any]] = [
    {
        "billing_id": "BIL-001",
        "user_id": "123-45-6789",
        "booking_id": "BK-001",
        "booking_type": "flight",
        "transaction_date": datetime.now().isoformat(),
        "subtotal": 550.00,
        "tax_amount": 48.00,
        "total_amount": 598.00,
        "payment_method": "credit_card",
        "payment_status": "completed",
        "card_last_four": "4242",
        "invoice_number": "INV-2025-001",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "billing_id": "BIL-002",
        "user_id": "123-45-6789",
        "booking_id": "BK-002",
        "booking_type": "hotel",
        "transaction_date": datetime.now().isoformat(),
        "subtotal": 520.00,
        "tax_amount": 47.00,
        "total_amount": 567.00,
        "payment_method": "credit_card",
        "payment_status": "completed",
        "card_last_four": "4242",
        "invoice_number": "INV-2025-002",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "billing_id": "BIL-003",
        "user_id": "234-56-7890",
        "booking_id": "BK-003",
        "booking_type": "car",
        "transaction_date": datetime.now().isoformat(),
        "subtotal": 245.00,
        "tax_amount": 22.00,
        "total_amount": 267.00,
        "payment_method": "paypal",
        "payment_status": "pending",
        "card_last_four": None,
        "invoice_number": "INV-2025-003",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    },
    {
        "billing_id": "BIL-004",
        "user_id": "123-45-6789",
        "booking_id": "BK-004",
        "booking_type": "flight",
        "transaction_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "subtotal": 320.00,
        "tax_amount": 29.00,
        "total_amount": 349.00,
        "payment_method": "debit_card",
        "payment_status": "completed",
        "card_last_four": "1234",
        "invoice_number": "INV-2024-104",
        "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=30)).isoformat(),
    },
    {
        "billing_id": "BIL-005",
        "user_id": "345-67-8901",
        "booking_id": "BK-005",
        "booking_type": "hotel",
        "transaction_date": (datetime.now() - timedelta(days=20)).isoformat(),
        "subtotal": 630.00,
        "tax_amount": 57.00,
        "total_amount": 687.00,
        "payment_method": "credit_card",
        "payment_status": "completed",
        "card_last_four": "5678",
        "invoice_number": "INV-2024-105",
        "created_at": (datetime.now() - timedelta(days=20)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=20)).isoformat(),
    },
]

# Sample reviews data
MOCK_REVIEWS: List[Dict[str, Any]] = [
    {
        "review_id": "REV-001",
        "user_id": "123-45-6789",
        "booking_id": "BK-004",
        "listing_id": "FLT-GHI321",
        "listing_type": "flight",
        "rating": 4.5,
        "title": "Great flight experience",
        "content": "Smooth flight, friendly crew, and on-time arrival. Would recommend!",
        "created_at": (datetime.now() - timedelta(days=8)).isoformat(),
    },
    {
        "review_id": "REV-002",
        "user_id": "345-67-8901",
        "booking_id": "BK-005",
        "listing_id": "HTL-JKL654",
        "listing_type": "hotel",
        "rating": 4.0,
        "title": "Nice stay, good location",
        "content": "Great hotel in a prime location. Rooms were clean and staff was helpful.",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
    },
]


# ==================== Mock Service Functions ====================

class MockBookingService:
    """
    Mock Booking Service - simulates Team 3's booking API
    Replace with real API calls when Team 3 provides endpoints
    """
    
    @staticmethod
    def get_user_bookings(user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        return [b for b in MOCK_BOOKINGS if b["user_id"] == user_id]
    
    @staticmethod
    def get_booking_by_id(booking_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific booking by ID"""
        for booking in MOCK_BOOKINGS:
            if booking["booking_id"] == booking_id:
                return booking
        return None
    
    @staticmethod
    def get_upcoming_bookings(user_id: str) -> List[Dict[str, Any]]:
        """Get upcoming bookings for a user"""
        now = datetime.now()
        return [
            b for b in MOCK_BOOKINGS 
            if b["user_id"] == user_id 
            and b["status"] in ["pending", "confirmed"]
            and datetime.fromisoformat(b["check_in_date"]) > now
        ]
    
    @staticmethod
    def get_past_bookings(user_id: str) -> List[Dict[str, Any]]:
        """Get past/completed bookings for a user"""
        return [
            b for b in MOCK_BOOKINGS 
            if b["user_id"] == user_id 
            and b["status"] in ["completed", "cancelled"]
        ]
    
    @staticmethod
    def create_booking(booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking"""
        booking = {
            "booking_id": f"BK-{uuid.uuid4().hex[:6].upper()}",
            **booking_data,
            "status": "pending",
            "booking_date": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        MOCK_BOOKINGS.append(booking)
        return booking
    
    @staticmethod
    def update_booking_status(booking_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update booking status"""
        for booking in MOCK_BOOKINGS:
            if booking["booking_id"] == booking_id:
                booking["status"] = status
                booking["updated_at"] = datetime.now().isoformat()
                return booking
        return None
    
    @staticmethod
    def cancel_booking(booking_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a booking"""
        return MockBookingService.update_booking_status(booking_id, "cancelled")
    
    @staticmethod
    def get_all_bookings(
        page: int = 1, 
        page_size: int = 20,
        status: Optional[str] = None,
        booking_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all bookings with pagination and filters"""
        filtered = MOCK_BOOKINGS
        
        if status:
            filtered = [b for b in filtered if b["status"] == status]
        if booking_type:
            filtered = [b for b in filtered if b["booking_type"] == booking_type]
        
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            "bookings": filtered[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }


class MockBillingService:
    """
    Mock Billing Service - simulates Team 4's billing API
    Replace with real API calls when Team 4 provides endpoints
    """
    
    @staticmethod
    def get_user_bills(user_id: str) -> List[Dict[str, Any]]:
        """Get all billing records for a user"""
        return [b for b in MOCK_BILLINGS if b["user_id"] == user_id]
    
    @staticmethod
    def get_bill_by_id(billing_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific billing record"""
        for bill in MOCK_BILLINGS:
            if bill["billing_id"] == billing_id:
                return bill
        return None
    
    @staticmethod
    def get_bill_by_booking(booking_id: str) -> Optional[Dict[str, Any]]:
        """Get billing record for a booking"""
        for bill in MOCK_BILLINGS:
            if bill["booking_id"] == booking_id:
                return bill
        return None
    
    @staticmethod
    def create_bill(billing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new billing record"""
        bill = {
            "billing_id": f"BIL-{uuid.uuid4().hex[:6].upper()}",
            **billing_data,
            "payment_status": "pending",
            "invoice_number": f"INV-{datetime.now().year}-{len(MOCK_BILLINGS) + 1:03d}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        MOCK_BILLINGS.append(bill)
        return bill
    
    @staticmethod
    def process_payment(billing_id: str) -> Optional[Dict[str, Any]]:
        """Process payment for a billing record"""
        for bill in MOCK_BILLINGS:
            if bill["billing_id"] == billing_id:
                bill["payment_status"] = "completed"
                bill["transaction_date"] = datetime.now().isoformat()
                bill["updated_at"] = datetime.now().isoformat()
                return bill
        return None
    
    @staticmethod
    def refund_payment(billing_id: str) -> Optional[Dict[str, Any]]:
        """Refund a payment"""
        for bill in MOCK_BILLINGS:
            if bill["billing_id"] == billing_id:
                bill["payment_status"] = "refunded"
                bill["updated_at"] = datetime.now().isoformat()
                return bill
        return None
    
    @staticmethod
    def search_bills(
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        payment_status: Optional[str] = None,
        booking_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search billing records"""
        filtered = MOCK_BILLINGS
        
        if start_date:
            start = datetime.fromisoformat(start_date)
            filtered = [b for b in filtered if datetime.fromisoformat(b["transaction_date"]) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            filtered = [b for b in filtered if datetime.fromisoformat(b["transaction_date"]) <= end]
        
        if payment_status:
            filtered = [b for b in filtered if b["payment_status"] == payment_status]
        
        if booking_type:
            filtered = [b for b in filtered if b["booking_type"] == booking_type]
        
        total = len(filtered)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return {
            "billings": filtered[start_idx:end_idx],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    @staticmethod
    def get_revenue_by_month(year: int) -> List[Dict[str, Any]]:
        """Get monthly revenue for admin reports"""
        # Generate sample monthly revenue
        months = []
        for month in range(1, 13):
            months.append({
                "month": month,
                "year": year,
                "total_revenue": random.uniform(50000, 150000),
                "flight_revenue": random.uniform(20000, 60000),
                "hotel_revenue": random.uniform(20000, 60000),
                "car_revenue": random.uniform(10000, 30000),
                "transaction_count": random.randint(100, 500),
            })
        return months
    
    @staticmethod
    def get_revenue_by_city(year: int) -> List[Dict[str, Any]]:
        """Get city-wise revenue for admin reports"""
        cities = [
            ("New York", "NY"),
            ("Los Angeles", "CA"),
            ("San Francisco", "CA"),
            ("Miami", "FL"),
            ("Chicago", "IL"),
            ("Seattle", "WA"),
            ("Boston", "MA"),
            ("Denver", "CO"),
            ("Austin", "TX"),
            ("Las Vegas", "NV"),
        ]
        
        return [
            {
                "city": city,
                "state": state,
                "year": year,
                "total_revenue": random.uniform(100000, 500000),
                "booking_count": random.randint(500, 2000),
            }
            for city, state in cities
        ]


class MockReviewService:
    """
    Mock Review Service - for user reviews
    """
    
    @staticmethod
    def get_listing_reviews(listing_id: str, listing_type: str) -> List[Dict[str, Any]]:
        """Get reviews for a listing"""
        return [
            r for r in MOCK_REVIEWS 
            if r["listing_id"] == listing_id and r["listing_type"] == listing_type
        ]
    
    @staticmethod
    def get_user_reviews(user_id: str) -> List[Dict[str, Any]]:
        """Get all reviews by a user"""
        return [r for r in MOCK_REVIEWS if r["user_id"] == user_id]
    
    @staticmethod
    def create_review(review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new review"""
        review = {
            "review_id": f"REV-{uuid.uuid4().hex[:6].upper()}",
            **review_data,
            "created_at": datetime.now().isoformat(),
        }
        MOCK_REVIEWS.append(review)
        return review


# ==================== Singleton Instances ====================

mock_booking_service = MockBookingService()
mock_billing_service = MockBillingService()
mock_review_service = MockReviewService()


# ==================== Helper Functions ====================

def get_booking_stats() -> Dict[str, Any]:
    """Get booking statistics for dashboard"""
    total = len(MOCK_BOOKINGS)
    pending = len([b for b in MOCK_BOOKINGS if b["status"] == "pending"])
    confirmed = len([b for b in MOCK_BOOKINGS if b["status"] == "confirmed"])
    completed = len([b for b in MOCK_BOOKINGS if b["status"] == "completed"])
    cancelled = len([b for b in MOCK_BOOKINGS if b["status"] == "cancelled"])
    
    return {
        "total_bookings": total,
        "pending": pending,
        "confirmed": confirmed,
        "completed": completed,
        "cancelled": cancelled,
    }


def get_billing_stats() -> Dict[str, Any]:
    """Get billing statistics for dashboard"""
    total_revenue = sum(b["total_amount"] for b in MOCK_BILLINGS if b["payment_status"] == "completed")
    pending_amount = sum(b["total_amount"] for b in MOCK_BILLINGS if b["payment_status"] == "pending")
    transaction_count = len(MOCK_BILLINGS)
    
    return {
        "total_revenue": total_revenue,
        "pending_amount": pending_amount,
        "transaction_count": transaction_count,
        "completed_transactions": len([b for b in MOCK_BILLINGS if b["payment_status"] == "completed"]),
        "pending_transactions": len([b for b in MOCK_BILLINGS if b["payment_status"] == "pending"]),
    }

