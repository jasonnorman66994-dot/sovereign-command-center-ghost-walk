CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    timestamp_utc DATETIME NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    geo_location JSON
);

-- Insert a test row for Los Angeles (lat: 34.0522, lon: -118.2437)
INSERT INTO alerts (alert_type, severity, timestamp_utc, user_email, geo_location)
VALUES ('test', 'medium', NOW(), 'la@example.com', JSON_OBJECT('lat', 34.0522, 'lon', -118.2437));

-- Insert a test row
INSERT INTO alerts (alert_type, severity, timestamp_utc, user_email, geo_location)
VALUES ('test', 'low', NOW(), 'test@example.com', JSON_OBJECT('lat', 0, 'lon', 0));
