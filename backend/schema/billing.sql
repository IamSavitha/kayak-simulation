CREATE TABLE billing (
    billing_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id          VARCHAR(11) NOT NULL,           -- SSN format '###-##-####'
    booking_type     ENUM('FLIGHT','HOTEL','CAR') NOT NULL,
    booking_id       BIGINT NOT NULL,
    transaction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount     DECIMAL(10,2) NOT NULL,
    currency         VARCHAR(3) NOT NULL DEFAULT 'USD',
    payment_method   ENUM('CREDIT_CARD','PAYPAL') NOT NULL,
    transaction_status ENUM('PENDING','COMPLETED','FAILED','REFUNDED','PARTIAL') 
        NOT NULL DEFAULT 'PENDING',
    invoice_ref      VARCHAR(64) NULL,
    metadata         JSON NULL,
    INDEX idx_user_date (user_id, transaction_date),
    INDEX idx_date (transaction_date),
    INDEX idx_month (transaction_date),
    INDEX idx_booking (booking_id),
    INDEX idx_status (transaction_status)
);
