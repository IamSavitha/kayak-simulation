-- Kayak Simulation Database Schema
-- Team 1: Users and Admins Tables
-- MySQL DDL Script

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS kayak_db;
USE kayak_db;

-- ========================================
-- USERS TABLE
-- ========================================
-- User ID follows SSN format: ###-##-####
-- Stores all user information as per project requirements

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(11) PRIMARY KEY COMMENT 'SSN format: ###-##-####',
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL COMMENT 'US State abbreviation',
    zip_code VARCHAR(10) NOT NULL COMMENT 'Format: ##### or #####-####',
    profile_image_url VARCHAR(500) DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT 'Bcrypt hashed password',
    
    -- Credit Card / Payment Details (encrypted in production)
    credit_card_number_encrypted VARCHAR(500) DEFAULT NULL,
    credit_card_last_four CHAR(4) DEFAULT NULL,
    credit_card_expiry VARCHAR(7) DEFAULT NULL COMMENT 'Format: MM/YYYY',
    credit_card_type VARCHAR(20) DEFAULT NULL COMMENT 'VISA, MASTERCARD, AMEX, etc.',
    billing_address VARCHAR(255) DEFAULT NULL,
    billing_city VARCHAR(100) DEFAULT NULL,
    billing_state CHAR(2) DEFAULT NULL,
    billing_zip_code VARCHAR(10) DEFAULT NULL,
    
    -- Account status and metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    
    -- Indexes for common queries
    INDEX idx_users_email (email),
    INDEX idx_users_state (state),
    INDEX idx_users_city (city),
    INDEX idx_users_created_at (created_at),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================
-- ADMINISTRATORS TABLE
-- ========================================
-- Admin accounts for system management

CREATE TABLE IF NOT EXISTS administrators (
    admin_id VARCHAR(36) PRIMARY KEY COMMENT 'UUID format',
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL COMMENT 'US State abbreviation',
    zip_code VARCHAR(10) NOT NULL COMMENT 'Format: ##### or #####-####',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Bcrypt hashed password',
    
    -- Role and access level
    role ENUM('SUPER_ADMIN', 'ADMIN', 'MODERATOR', 'ANALYST') NOT NULL DEFAULT 'ADMIN',
    access_level INT NOT NULL DEFAULT 1 COMMENT '1-10, higher = more access',
    
    -- Reports and analytics permissions
    can_manage_users BOOLEAN DEFAULT TRUE,
    can_manage_listings BOOLEAN DEFAULT TRUE,
    can_view_billing BOOLEAN DEFAULT TRUE,
    can_view_analytics BOOLEAN DEFAULT TRUE,
    can_manage_admins BOOLEAN DEFAULT FALSE COMMENT 'Only SUPER_ADMIN',
    
    -- Account status and metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    created_by VARCHAR(36) DEFAULT NULL COMMENT 'Admin who created this account',
    
    -- Indexes
    INDEX idx_admins_email (email),
    INDEX idx_admins_role (role),
    INDEX idx_admins_active (is_active),
    
    -- Foreign key to track who created the admin
    FOREIGN KEY (created_by) REFERENCES administrators(admin_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================
-- ADMIN SESSIONS TABLE
-- ========================================
-- For managing admin login sessions

CREATE TABLE IF NOT EXISTS admin_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    admin_id VARCHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    user_agent VARCHAR(500) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    INDEX idx_sessions_admin (admin_id),
    INDEX idx_sessions_expires (expires_at),
    INDEX idx_sessions_active (is_active),
    
    FOREIGN KEY (admin_id) REFERENCES administrators(admin_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================
-- USER SESSIONS TABLE
-- ========================================
-- For managing user login sessions

CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(11) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    user_agent VARCHAR(500) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    INDEX idx_user_sessions_user (user_id),
    INDEX idx_user_sessions_expires (expires_at),
    INDEX idx_user_sessions_active (is_active),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================
-- PASSWORD RESET TOKENS
-- ========================================
-- For password recovery functionality

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(11) DEFAULT NULL,
    admin_id VARCHAR(36) DEFAULT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    
    INDEX idx_reset_user (user_id),
    INDEX idx_reset_admin (admin_id),
    INDEX idx_reset_expires (expires_at),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES administrators(admin_id) ON DELETE CASCADE,
    
    CHECK (
        (user_id IS NOT NULL AND admin_id IS NULL) OR 
        (user_id IS NULL AND admin_id IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================
-- ADMIN ACTIVITY LOG
-- ========================================
-- Track admin actions for audit purposes

CREATE TABLE IF NOT EXISTS admin_activity_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_id VARCHAR(36) NOT NULL,
    action_type ENUM(
        'LOGIN', 'LOGOUT', 
        'CREATE_USER', 'UPDATE_USER', 'DELETE_USER',
        'CREATE_LISTING', 'UPDATE_LISTING', 'DELETE_LISTING',
        'VIEW_BILLING', 'MODIFY_BILLING',
        'VIEW_REPORT', 'EXPORT_REPORT',
        'CREATE_ADMIN', 'UPDATE_ADMIN', 'DELETE_ADMIN'
    ) NOT NULL,
    entity_type VARCHAR(50) DEFAULT NULL COMMENT 'user, listing, billing, etc.',
    entity_id VARCHAR(50) DEFAULT NULL COMMENT 'ID of affected entity',
    details JSON DEFAULT NULL COMMENT 'Additional action details',
    ip_address VARCHAR(45) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_activity_admin (admin_id),
    INDEX idx_activity_type (action_type),
    INDEX idx_activity_entity (entity_type, entity_id),
    INDEX idx_activity_created (created_at),
    
    FOREIGN KEY (admin_id) REFERENCES administrators(admin_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================
-- STORED PROCEDURES
-- ========================================

-- Procedure to validate SSN format
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS validate_ssn(IN ssn VARCHAR(11), OUT is_valid BOOLEAN)
BEGIN
    SET is_valid = (ssn REGEXP '^[0-9]{3}-[0-9]{2}-[0-9]{4}$');
END //
DELIMITER ;

-- Procedure to validate ZIP code format
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS validate_zip_code(IN zip VARCHAR(10), OUT is_valid BOOLEAN)
BEGIN
    SET is_valid = (zip REGEXP '^[0-9]{5}$' OR zip REGEXP '^[0-9]{5}-[0-9]{4}$');
END //
DELIMITER ;

-- Procedure to get user with masked SSN
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS get_user_masked(IN p_user_id VARCHAR(11))
BEGIN
    SELECT 
        CONCAT('***-**-', RIGHT(user_id, 4)) as user_id_masked,
        first_name,
        last_name,
        email,
        phone_number,
        address,
        city,
        state,
        zip_code,
        profile_image_url,
        CASE 
            WHEN credit_card_last_four IS NOT NULL 
            THEN CONCAT('****-****-****-', credit_card_last_four)
            ELSE NULL 
        END as credit_card_masked,
        credit_card_type,
        is_active,
        is_verified,
        created_at,
        updated_at,
        last_login_at
    FROM users
    WHERE user_id = p_user_id;
END //
DELIMITER ;


-- ========================================
-- TRIGGERS
-- ========================================

-- Trigger to validate user data before insert
DELIMITER //
CREATE TRIGGER IF NOT EXISTS before_user_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    -- Validate SSN format
    IF NOT (NEW.user_id REGEXP '^[0-9]{3}-[0-9]{2}-[0-9]{4}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid SSN format. Expected: ###-##-####';
    END IF;
    
    -- Validate ZIP code format
    IF NOT (NEW.zip_code REGEXP '^[0-9]{5}$' OR NEW.zip_code REGEXP '^[0-9]{5}-[0-9]{4}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid ZIP code format. Expected: ##### or #####-####';
    END IF;
    
    -- Validate state abbreviation (basic check for 2 uppercase letters)
    IF NOT (NEW.state REGEXP '^[A-Z]{2}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid state abbreviation. Expected: 2-letter US state code';
    END IF;
END //
DELIMITER ;

-- Trigger to validate user data before update
DELIMITER //
CREATE TRIGGER IF NOT EXISTS before_user_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    -- Validate ZIP code format
    IF NOT (NEW.zip_code REGEXP '^[0-9]{5}$' OR NEW.zip_code REGEXP '^[0-9]{5}-[0-9]{4}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid ZIP code format. Expected: ##### or #####-####';
    END IF;
    
    -- Validate state abbreviation
    IF NOT (NEW.state REGEXP '^[A-Z]{2}$') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid state abbreviation. Expected: 2-letter US state code';
    END IF;
END //
DELIMITER ;


-- ========================================
-- INITIAL DATA - DEFAULT SUPER ADMIN
-- ========================================

-- Insert default super admin (password: admin123 - change in production!)
-- Password hash for 'admin123' using bcrypt (same as Team 5)
INSERT INTO administrators (
    admin_id, first_name, last_name, email, phone_number,
    address, city, state, zip_code, password_hash,
    role, access_level, can_manage_users, can_manage_listings,
    can_view_billing, can_view_analytics, can_manage_admins
) VALUES (
    'ADMIN-001',
    'System', 'Admin', 'admin@kayak.com', '(555) 000-0001',
    '123 Admin Street', 'San Jose', 'CA', '95112',
    '$2b$12$owAeUsE4obr0PXhnX9YdMuMb4rNd8TUe7A.slfY8ogZicrvhRUIa6',
    'SUPER_ADMIN', 10, TRUE, TRUE, TRUE, TRUE, TRUE
) ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- Create alias view for Team 5 compatibility (they use 'admins' table name)
CREATE OR REPLACE VIEW admins AS SELECT * FROM administrators;


-- ========================================
-- VIEWS
-- ========================================

-- View for user summary (without sensitive data)
CREATE OR REPLACE VIEW user_summary AS
SELECT 
    CONCAT('***-**-', RIGHT(user_id, 4)) as user_id_masked,
    first_name,
    last_name,
    email,
    city,
    state,
    is_active,
    is_verified,
    created_at
FROM users;

-- View for admin summary
CREATE OR REPLACE VIEW admin_summary AS
SELECT 
    admin_id,
    first_name,
    last_name,
    email,
    role,
    access_level,
    is_active,
    created_at,
    last_login_at
FROM administrators;

-- View for recent admin activity
CREATE OR REPLACE VIEW recent_admin_activity AS
SELECT 
    al.log_id,
    al.admin_id,
    CONCAT(a.first_name, ' ', a.last_name) as admin_name,
    al.action_type,
    al.entity_type,
    al.entity_id,
    al.ip_address,
    al.created_at
FROM admin_activity_log al
JOIN administrators a ON al.admin_id = a.admin_id
ORDER BY al.created_at DESC
LIMIT 100;


-- ========================================
-- PERFORMANCE INDEXES
-- ========================================

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_users_location ON users(state, city);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(is_active, is_verified);
CREATE INDEX IF NOT EXISTS idx_admins_role_active ON administrators(role, is_active);

-- Fulltext index for user search
ALTER TABLE users ADD FULLTEXT INDEX ft_users_name (first_name, last_name);

COMMIT;


