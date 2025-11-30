-- Cars Table DDL
CREATE DATABASE IF NOT EXISTS kayak_listings;
USE kayak_listings;

CREATE TABLE IF NOT EXISTS cars (
    car_id VARCHAR(50) PRIMARY KEY,
    car_type VARCHAR(50) NOT NULL,
    company_provider_name VARCHAR(100) NOT NULL,
    model_and_year VARCHAR(100) NOT NULL,
    transmission_type ENUM('Automatic', 'Manual') NOT NULL DEFAULT 'Automatic',
    number_of_seats INT NOT NULL,
    daily_rental_price DECIMAL(10, 2) NOT NULL,
    car_rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    availability_status ENUM('Available', 'Unavailable', 'Reserved') DEFAULT 'Available',
    location_city VARCHAR(100),
    location_state VARCHAR(2),
    location_address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_car_type (car_type),
    INDEX idx_provider (company_provider_name),
    INDEX idx_transmission (transmission_type),
    INDEX idx_seats (number_of_seats),
    INDEX idx_price (daily_rental_price),
    INDEX idx_rating (car_rating),
    INDEX idx_status (availability_status),
    INDEX idx_location (location_city, location_state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

