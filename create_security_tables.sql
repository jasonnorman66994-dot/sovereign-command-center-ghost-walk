CREATE TABLE IF NOT EXISTS auth_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255),
    email VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    method VARCHAR(50),
    result VARCHAR(20),
    failure_reason VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    device_fingerprint VARCHAR(255),
    session_id VARCHAR(255),
    risk_score INT DEFAULT 0,
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id),
    INDEX idx_ip (ip_address),
    INDEX idx_result (result)
);

CREATE TABLE IF NOT EXISTS token_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    token_id VARCHAR(255) UNIQUE,
    user_id VARCHAR(255),
    token_type VARCHAR(50),
    ip_address VARCHAR(45),
    action VARCHAR(50),
    expires_at DATETIME,
    last_used_at DATETIME,
    last_used_ip VARCHAR(45),
    last_used_location VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_token_id (token_id),
    INDEX idx_user_id (user_id),
    INDEX idx_expires (expires_at)
);

CREATE TABLE IF NOT EXISTS email_auth_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    email VARCHAR(255),
    auth_type VARCHAR(50),
    code VARCHAR(255),
    request_ip VARCHAR(45),
    request_location VARCHAR(255),
    used BOOLEAN DEFAULT FALSE,
    used_at DATETIME,
    used_ip VARCHAR(45),
    used_location VARCHAR(255),
    expires_at DATETIME,
    attempts INT DEFAULT 0,
    INDEX idx_email (email),
    INDEX idx_code (code),
    INDEX idx_expires (expires_at)
);

CREATE TABLE IF NOT EXISTS cookie_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    cookie_id VARCHAR(255) UNIQUE,
    user_id VARCHAR(255),
    cookie_name VARCHAR(100),
    created_ip VARCHAR(45),
    created_location VARCHAR(255),
    last_seen_ip VARCHAR(45),
    last_seen_location VARCHAR(255),
    last_seen_at DATETIME,
    expires_at DATETIME,
    is_secure BOOLEAN DEFAULT TRUE,
    is_httponly BOOLEAN DEFAULT TRUE,
    samesite VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    device_fingerprint VARCHAR(255),
    user_agent TEXT,
    INDEX idx_cookie_id (cookie_id),
    INDEX idx_user_id (user_id),
    INDEX idx_expires (expires_at)
);

CREATE TABLE IF NOT EXISTS security_alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(100),
    severity VARCHAR(20),
    user_id VARCHAR(255),
    ip_address VARCHAR(45),
    description TEXT,
    evidence JSON,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    resolved_by VARCHAR(255),
    INDEX idx_timestamp (timestamp),
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved)
);

CREATE TABLE IF NOT EXISTS alert_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255),
    sql_condition TEXT,
    severity VARCHAR(20),
    enabled BOOLEAN DEFAULT TRUE
);
