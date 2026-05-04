IF OBJECT_ID('alerts', 'U') IS NOT NULL
    DROP TABLE alerts;
GO

CREATE TABLE alerts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id NVARCHAR(255),
    email NVARCHAR(255),
    ip_address NVARCHAR(45),
    country NVARCHAR(64),
    city NVARCHAR(128),
    latitude NVARCHAR(32),
    longitude NVARCHAR(32),
    user_agent NVARCHAR(MAX),
    method NVARCHAR(32),
    result NVARCHAR(32),
    failure_reason NVARCHAR(255),
    risk_score INT,
    alert_time DATETIME DEFAULT GETDATE(),
    alert_channel NVARCHAR(64),
    telegram_status NVARCHAR(32),
    baseline_value FLOAT,
    deviation_score FLOAT
);
GO
