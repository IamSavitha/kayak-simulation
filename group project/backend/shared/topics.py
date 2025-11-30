"""
Kafka Topic Definitions - Aligned with Team 5's topics.py

This file defines all Kafka topics used across the Kayak Simulation system.
Topic names are standardized across all teams for proper inter-service communication.

IMPORTANT: All topics use the "kayak." prefix as per Team 5's standard!
"""


class KafkaTopics:
    """
    Centralized Kafka topic names.
    Aligned with Team 5's topics.py - ALL topics use 'kayak.' prefix!
    """
    
    # ==================== User Events ====================
    USER_CREATED = "kayak.user.created"
    USER_UPDATED = "kayak.user.updated"
    USER_DELETED = "kayak.user.deleted"
    
    # ==================== Search Events ====================
    FLIGHT_SEARCH = "kayak.search.flight"
    HOTEL_SEARCH = "kayak.search.hotel"
    CAR_SEARCH = "kayak.search.car"
    
    # ==================== Booking Events (Team 3) ====================
    BOOKING_CREATED = "kayak.booking.created"
    BOOKING_UPDATED = "kayak.booking.updated"
    BOOKING_CANCELLED = "kayak.booking.cancelled"
    BOOKING_COMPLETED = "kayak.booking.completed"
    
    # ==================== Payment/Billing Events (Team 4) ====================
    PAYMENT_INITIATED = "kayak.payment.initiated"
    PAYMENT_COMPLETED = "kayak.payment.completed"
    PAYMENT_FAILED = "kayak.payment.failed"
    PAYMENT_REFUNDED = "kayak.payment.refunded"
    
    # ==================== Listing Events (Team 2) ====================
    FLIGHT_CREATED = "kayak.listing.flight.created"
    FLIGHT_UPDATED = "kayak.listing.flight.updated"
    HOTEL_CREATED = "kayak.listing.hotel.created"
    HOTEL_UPDATED = "kayak.listing.hotel.updated"
    CAR_CREATED = "kayak.listing.car.created"
    CAR_UPDATED = "kayak.listing.car.updated"
    
    # ==================== Review Events ====================
    REVIEW_CREATED = "kayak.review.created"
    REVIEW_UPDATED = "kayak.review.updated"
    REVIEW_DELETED = "kayak.review.deleted"
    
    # ==================== Analytics Events (Team 5) ====================
    PAGE_VIEW = "kayak.analytics.pageview"
    CLICK_EVENT = "kayak.analytics.click"
    SEARCH_EVENT = "kayak.analytics.search"
    
    # ==================== AI Deals Agent Topics (Team 1) ====================
    RAW_SUPPLIER_FEEDS = "kayak.ai.raw_supplier_feeds"
    DEALS_NORMALIZED = "kayak.ai.deals.normalized"
    DEALS_SCORED = "kayak.ai.deals.scored"
    DEALS_TAGGED = "kayak.ai.deals.tagged"
    DEAL_EVENTS = "kayak.ai.deal.events"
    
    # ==================== Notification Events ====================
    NOTIFICATION_EMAIL = "kayak.notification.email"
    NOTIFICATION_SMS = "kayak.notification.sms"
    NOTIFICATION_PUSH = "kayak.notification.push"
    
    @classmethod
    def all_topics(cls) -> list:
        """Get all topic names."""
        return [
            value for name, value in vars(cls).items()
            if not name.startswith('_') and isinstance(value, str)
        ]
    
    @classmethod
    def user_topics(cls) -> list:
        """Get user-related topics."""
        return [cls.USER_CREATED, cls.USER_UPDATED, cls.USER_DELETED]
    
    @classmethod
    def booking_topics(cls) -> list:
        """Get booking-related topics."""
        return [
            cls.BOOKING_CREATED, cls.BOOKING_UPDATED,
            cls.BOOKING_CANCELLED, cls.BOOKING_COMPLETED
        ]
    
    @classmethod
    def payment_topics(cls) -> list:
        """Get payment-related topics."""
        return [
            cls.PAYMENT_INITIATED, cls.PAYMENT_COMPLETED,
            cls.PAYMENT_FAILED, cls.PAYMENT_REFUNDED
        ]
    
    @classmethod
    def ai_topics(cls) -> list:
        """Get AI service topics."""
        return [
            cls.RAW_SUPPLIER_FEEDS, cls.DEALS_NORMALIZED,
            cls.DEALS_SCORED, cls.DEALS_TAGGED, cls.DEAL_EVENTS
        ]


# Legacy aliases for backward compatibility
SUPPLIER_FEEDS = KafkaTopics.RAW_SUPPLIER_FEEDS

