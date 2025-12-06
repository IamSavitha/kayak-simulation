-- Kayak Simulation Database Schema
-- MySQL 8.0+

CREATE DATABASE IF NOT EXISTS kayak_db;
USE kayak_db;

-- ==================== Users Table ====================
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(11) PRIMARY KEY,  -- SSN format: XXX-XX-XXXX
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    profile_image_url VARCHAR(500),
    credit_card_last_four VARCHAR(4),
    credit_card_type VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_email (email),
    INDEX idx_user_name (first_name, last_name)
);

-- ==================== Flights Table ====================
CREATE TABLE IF NOT EXISTS flights (
    flight_id VARCHAR(10) PRIMARY KEY,  -- e.g., AA123
    airline_name VARCHAR(100) NOT NULL,
    operator_name VARCHAR(100),
    departure_airport VARCHAR(5) NOT NULL,
    arrival_airport VARCHAR(5) NOT NULL,
    departure_datetime DATETIME NOT NULL,
    arrival_datetime DATETIME NOT NULL,
    duration_minutes INT,
    flight_class ENUM('economy', 'business', 'first') DEFAULT 'economy',
    base_price DECIMAL(10, 2) NOT NULL,
    total_seats INT NOT NULL,
    available_seats INT NOT NULL,
    rating FLOAT DEFAULT 0.0,
    total_reviews INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_flight_route (departure_airport, arrival_airport),
    INDEX idx_flight_date (departure_datetime),
    INDEX idx_flight_airline (airline_name)
);

-- ==================== Hotels Table ====================
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id VARCHAR(50) PRIMARY KEY,
    hotel_name VARCHAR(200) NOT NULL,
    description TEXT,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2),
    zip_code VARCHAR(10),
    star_rating INT CHECK (star_rating BETWEEN 1 AND 5),
    rating FLOAT DEFAULT 0.0,
    total_reviews INT DEFAULT 0,
    amenities TEXT,  -- Comma-separated
    phone_number VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_hotel_location (city, state),
    INDEX idx_hotel_rating (star_rating)
);

-- ==================== Hotel Rooms Table ====================
CREATE TABLE IF NOT EXISTS hotel_rooms (
    room_id VARCHAR(50) PRIMARY KEY,
    hotel_id VARCHAR(50) NOT NULL,
    room_type ENUM('single', 'double', 'suite', 'deluxe') NOT NULL,
    room_number VARCHAR(10),
    price_per_night DECIMAL(10, 2) NOT NULL,
    max_occupancy INT DEFAULT 2,
    total_rooms INT DEFAULT 1,
    available_rooms INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE,
    INDEX idx_room_hotel (hotel_id)
);

-- ==================== Cars Table ====================
CREATE TABLE IF NOT EXISTS cars (
    car_id VARCHAR(50) PRIMARY KEY,
    car_type ENUM('sedan', 'suv', 'compact', 'luxury', 'van') NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    transmission_type ENUM('automatic', 'manual') DEFAULT 'automatic',
    seats INT NOT NULL,
    doors INT DEFAULT 4,
    daily_rental_price DECIMAL(10, 2) NOT NULL,
    pickup_location VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(2),
    rating FLOAT DEFAULT 0.0,
    total_reviews INT DEFAULT 0,
    image_url VARCHAR(500),
    is_available BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_car_location (city, state),
    INDEX idx_car_provider (provider_name),
    INDEX idx_car_type (car_type)
);

-- ==================== Bookings Table ====================
CREATE TABLE IF NOT EXISTS bookings (
    booking_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(11) NOT NULL,
    booking_type ENUM('flight', 'hotel', 'car') NOT NULL,
    listing_id VARCHAR(50) NOT NULL,
    check_in_date DATETIME NOT NULL,
    check_out_date DATETIME,
    num_passengers INT DEFAULT 1,
    num_rooms INT DEFAULT 1,
    num_nights INT DEFAULT 1,
    status ENUM('pending', 'confirmed', 'cancelled', 'completed', 'refund_pending') DEFAULT 'pending',
    total_price DECIMAL(10, 2) NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_booking_user (user_id),
    INDEX idx_booking_type (booking_type),
    INDEX idx_booking_date (booking_date),
    INDEX idx_booking_status (status)
);

-- ==================== Billings Table ====================
CREATE TABLE IF NOT EXISTS billings (
    billing_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(11) NOT NULL,
    booking_id VARCHAR(50) NOT NULL,
    booking_type ENUM('flight', 'hotel', 'car') NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('credit_card', 'debit_card', 'paypal', 'bank_transfer') NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    card_last_four VARCHAR(4),
    invoice_number VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    INDEX idx_billing_user (user_id),
    INDEX idx_billing_date (transaction_date),
    INDEX idx_billing_status (payment_status)
);

-- ==================== Admins Table ====================
CREATE TABLE IF NOT EXISTS admins (
    admin_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    profile_image_url VARCHAR(500),
    role ENUM('super_admin', 'admin', 'moderator') DEFAULT 'admin',
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    INDEX idx_admin_email (email)
);

-- ==================== Default Admin User ====================
INSERT INTO admins (admin_id, first_name, last_name, email, password_hash, role)
VALUES ('ADMIN-001', 'System', 'Admin', 'admin@kayak.com', 
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiOQ.7N0S2lG',  -- password: admin123
        'super_admin')
ON DUPLICATE KEY UPDATE admin_id = admin_id;

