
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'alert_rules')
BEGIN
    CREATE TABLE alert_rules (
        rule_id INT IDENTITY(1,1) PRIMARY KEY,
        description VARCHAR(255),
        sql_condition NVARCHAR(MAX),
        severity VARCHAR(20),
        enabled BIT DEFAULT 1
    );
END


INSERT INTO alert_rules (description, sql_condition, severity) VALUES
('More than 3 failed logins from same IP in 10 min',
 'SELECT 1 FROM auth_logs WHERE result = ''failed'' AND timestamp >= DATEADD(MINUTE, -10, GETDATE()) GROUP BY ip_address HAVING COUNT(*) > 3',
 'HIGH'),
('Multiple accounts accessed from same device in 1 hour',
 'SELECT 1 FROM auth_logs WHERE result = ''success'' AND timestamp >= DATEADD(HOUR, -1, GETDATE()) GROUP BY device_id HAVING COUNT(DISTINCT user_id) > 3',
 'MEDIUM'),
('User logged in from new country',
 'SELECT 1 FROM auth_logs WHERE result = ''success'' AND country_code <> last_known_country',
 'MEDIUM'),
('Multiple password reset requests in 30 min',
 'SELECT 1 FROM password_reset_logs WHERE timestamp >= DATEADD(MINUTE, -30, GETDATE()) GROUP BY user_id HAVING COUNT(*) > 2',
 'LOW'),
('Admin login outside business hours',
 'SELECT 1 FROM auth_logs WHERE result = ''success'' AND role = ''admin'' AND (DATEPART(HOUR, timestamp) < 8 OR DATEPART(HOUR, timestamp) > 18)',
 'HIGH');
