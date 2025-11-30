// MongoDB Initialization Script
// Aligned with Team 5's 01_init.js
// Run with: mongosh < init.js

// Switch to kayak database
db = db.getSiblingDB('kayak_db');

// ==================== Reviews Collection ====================
db.createCollection('reviews');
db.reviews.createIndex({ "user_id": 1 });
db.reviews.createIndex({ "listing_id": 1 });
db.reviews.createIndex({ "listing_type": 1 });
db.reviews.createIndex({ "created_at": -1 });
db.reviews.createIndex({ "rating": -1 });

// Sample review schema:
// {
//   user_id: "123-45-6789",
//   listing_id: "FL001",
//   listing_type: "flight|hotel|car",
//   rating: 4.5,
//   title: "Great experience",
//   content: "Detailed review...",
//   helpful_votes: 10,
//   created_at: ISODate(),
//   updated_at: ISODate()
// }

// ==================== Images Collection ====================
db.createCollection('images');
db.images.createIndex({ "listing_id": 1 });
db.images.createIndex({ "listing_type": 1 });
db.images.createIndex({ "user_id": 1 });

// Sample image schema:
// {
//   listing_id: "HOTEL001",
//   listing_type: "hotel",
//   url: "https://...",
//   thumbnail_url: "https://...",
//   caption: "Room view",
//   order: 1,
//   uploaded_at: ISODate()
// }

// ==================== General Logs Collection ====================
db.createCollection('logs');
db.logs.createIndex({ "timestamp": -1 });
db.logs.createIndex({ "user_id": 1 });
db.logs.createIndex({ "action": 1 });
db.logs.createIndex({ "level": 1 });

// ==================== User Behavior Logs Collection ====================
db.createCollection('user_logs');
db.user_logs.createIndex({ "user_id": 1 });
db.user_logs.createIndex({ "session_id": 1 });
db.user_logs.createIndex({ "timestamp": -1 });
db.user_logs.createIndex({ "event_type": 1 });

// Sample user log schema:
// {
//   user_id: "123-45-6789",
//   session_id: "sess_abc123",
//   event_type: "page_view|click|search",
//   page: "/flights",
//   element_id: "search-btn",
//   metadata: {},
//   timestamp: ISODate()
// }

// ==================== Search Logs Collection ====================
db.createCollection('search_logs');
db.search_logs.createIndex({ "user_id": 1 });
db.search_logs.createIndex({ "search_type": 1 });
db.search_logs.createIndex({ "timestamp": -1 });
db.search_logs.createIndex({ "origin": 1, "destination": 1 });

// Sample search log schema:
// {
//   user_id: "123-45-6789",
//   session_id: "sess_abc123",
//   search_type: "flight|hotel|car",
//   query: {
//     origin: "SFO",
//     destination: "LAX",
//     departure_date: "2025-01-15",
//     passengers: 2
//   },
//   results_count: 25,
//   timestamp: ISODate()
// }

// ==================== Booking Logs Collection ====================
db.createCollection('booking_logs');
db.booking_logs.createIndex({ "user_id": 1 });
db.booking_logs.createIndex({ "booking_id": 1 });
db.booking_logs.createIndex({ "timestamp": -1 });
db.booking_logs.createIndex({ "status": 1 });

// ==================== Analytics Collection ====================
db.createCollection('analytics');
db.analytics.createIndex({ "metric_type": 1 });
db.analytics.createIndex({ "timestamp": -1 });
db.analytics.createIndex({ "period_type": 1 });
db.analytics.createIndex({ "entity_type": 1 });

// Sample analytics schema:
// {
//   metric_type: "revenue|bookings|searches",
//   entity_type: "flight|hotel|car|all",
//   period_type: "daily|weekly|monthly|yearly",
//   period_start: ISODate(),
//   period_end: ISODate(),
//   value: 12500.00,
//   metadata: {
//     city: "San Jose",
//     state: "CA"
//   },
//   timestamp: ISODate()
// }

// ==================== Click Tracking Collection ====================
db.createCollection('click_tracking');
db.click_tracking.createIndex({ "session_id": 1 });
db.click_tracking.createIndex({ "page_name": 1 });
db.click_tracking.createIndex({ "timestamp": -1 });
db.click_tracking.createIndex({ "element_type": 1 });

// Sample click tracking schema:
// {
//   session_id: "sess_abc123",
//   user_id: "123-45-6789",
//   page_name: "/hotels/search",
//   element_id: "filter-stars-5",
//   element_type: "button|link|filter",
//   x_position: 150,
//   y_position: 320,
//   timestamp: ISODate()
// }

// ==================== User Journeys Collection ====================
db.createCollection('user_journeys');
db.user_journeys.createIndex({ "user_id": 1 });
db.user_journeys.createIndex({ "session_id": 1 });
db.user_journeys.createIndex({ "conversion": 1 });
db.user_journeys.createIndex({ "start_time": -1 });

// Sample user journey schema:
// {
//   user_id: "123-45-6789",
//   session_id: "sess_abc123",
//   start_time: ISODate(),
//   end_time: ISODate(),
//   pages_visited: ["/", "/flights", "/flights/search", "/checkout"],
//   conversion: true,
//   booking_id: "BK001",
//   total_time_seconds: 450,
//   device_type: "desktop|mobile|tablet"
// }

// ==================== AI Deals Cache Collection ====================
db.createCollection('ai_deals_cache');
db.ai_deals_cache.createIndex({ "deal_id": 1 }, { unique: true });
db.ai_deals_cache.createIndex({ "listing_type": 1 });
db.ai_deals_cache.createIndex({ "score": -1 });
db.ai_deals_cache.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });

// Sample deal cache schema:
// {
//   deal_id: "DEAL001",
//   listing_id: "FL001",
//   listing_type: "flight|hotel",
//   original_price: 500,
//   deal_price: 399,
//   discount_percent: 20.2,
//   score: 85,
//   tags: ["pet-friendly", "refundable"],
//   expires_at: ISODate()
// }

// ==================== User Watch List Collection ====================
db.createCollection('user_watches');
db.user_watches.createIndex({ "user_id": 1 });
db.user_watches.createIndex({ "listing_id": 1 });
db.user_watches.createIndex({ "is_active": 1 });
db.user_watches.createIndex({ "price_threshold": 1 });

// Sample watch schema:
// {
//   user_id: "123-45-6789",
//   listing_id: "FL001",
//   listing_type: "flight",
//   price_threshold: 400,
//   inventory_threshold: 5,
//   is_active: true,
//   created_at: ISODate()
// }

print("MongoDB collections and indexes created successfully!");
print("Collections created:");
print("  - reviews");
print("  - images");
print("  - logs");
print("  - user_logs");
print("  - search_logs");
print("  - booking_logs");
print("  - analytics");
print("  - click_tracking");
print("  - user_journeys");
print("  - ai_deals_cache");
print("  - user_watches");

