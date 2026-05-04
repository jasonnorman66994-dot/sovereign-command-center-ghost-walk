<?php
// test_login_logger.php - Standalone test for logAuthAttempt
require_once 'login_logger.php';

// Simulate a login attempt from a non-allowed country
$_SERVER['REMOTE_ADDR'] = '51.15.0.1'; // Example: France IP
$_SERVER['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';
$_SERVER['HTTP_ACCEPT_LANGUAGE'] = 'fr-FR,fr;q=0.9';
$_SERVER['HTTP_ACCEPT_ENCODING'] = 'gzip, deflate, br';

// Mock session_id() if not running in a real session
define('PHP_SESSION_ACTIVE', 2);
if (!function_exists('session_id')) {
    function session_id() { return 'testsessionid'; }
}

// Mock $pdo (replace with your real DB connection in production)
$pdo = new PDO('sqlite::memory:');
$pdo->exec("CREATE TABLE IF NOT EXISTS auth_logs (
    user_id TEXT, email TEXT, ip_address TEXT, user_agent TEXT, method TEXT, result TEXT,
    failure_reason TEXT, country TEXT, city TEXT, latitude TEXT, longitude TEXT,
    device_fingerprint TEXT, session_id TEXT, risk_score INTEGER
)");

// Call the logger
logAuthAttempt('testuser', 'test@example.com', 'password', 'failed', 'Invalid password');
echo "Test login attempt logged. Check your email and error log for alert.\n";
?>
