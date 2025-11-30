-- Hotels Table DDL
CREATE DATABASE IF NOT EXISTS kayak_listings;
USE kayak_listings;

CREATE TABLE IF NOT EXISTS hotels (
    hotel_id VARCHAR(50) PRIMARY KEY,
    hotel_name VARCHAR(200) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    star_rating INT NOT NULL CHECK (star_rating BETWEEN 1 AND 5),
    number_of_rooms INT NOT NULL DEFAULT 0,
    current_available_rooms INT NOT NULL DEFAULT 0,
    room_type VARCHAR(50) NOT NULL,
    price_per_night DECIMAL(10, 2) NOT NULL,
    amenities TEXT,
    hotel_rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_state (state),
    INDEX idx_star_rating (star_rating),
    INDEX idx_price (price_per_night),
    INDEX idx_rating (hotel_rating),
    INDEX idx_location (city, state),
    FULLTEXT idx_amenities (amenities)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

