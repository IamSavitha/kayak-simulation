-- Flights Table DDL
CREATE DATABASE IF NOT EXISTS kayak_listings;
USE kayak_listings;

CREATE TABLE IF NOT EXISTS flights (
    flight_id VARCHAR(50) PRIMARY KEY,
    airline VARCHAR(100) NOT NULL,
    departure_airport VARCHAR(10) NOT NULL,
    arrival_airport VARCHAR(10) NOT NULL,
    departure_date_time DATETIME NOT NULL,
    arrival_date_time DATETIME NOT NULL,
    duration_minutes INT NOT NULL,
    flight_class ENUM('Economy', 'Business', 'First') NOT NULL DEFAULT 'Economy',
    ticket_price DECIMAL(10, 2) NOT NULL,
    total_available_seats INT NOT NULL DEFAULT 0,
    current_available_seats INT NOT NULL DEFAULT 0,
    flight_rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_departure_airport (departure_airport),
    INDEX idx_arrival_airport (arrival_airport),
    INDEX idx_departure_date (departure_date_time),
    INDEX idx_price (ticket_price),
    INDEX idx_class (flight_class),
    INDEX idx_rating (flight_rating),
    INDEX idx_airline (airline)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

