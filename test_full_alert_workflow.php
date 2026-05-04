<?php
// test_full_alert_workflow.php - Triggers a geo-fence alert for all channels
require_once 'login_logger.php';

// Simulate a login attempt from a non-allowed country (France IP)
$_SERVER['REMOTE_ADDR'] = '51.15.0.1';
$_SERVER['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';
$_SERVER['HTTP_ACCEPT_LANGUAGE'] = 'fr-FR,fr;q=0.9';
$_SERVER['HTTP_ACCEPT_ENCODING'] = 'gzip, deflate, br';

// Mock session_id() if not running in a real session
define('PHP_SESSION_ACTIVE', 2);
if (!function_exists('session_id')) {
    function session_id() { return 'testsessionid'; }
}

// Mock $pdo (replace with your real DB connection in production)
$pdo = new PDO('mysql:host=localhost;dbname=yourdb', 'youruser', 'yourpassword');

// Call the logger
logAuthAttempt('testuser', 'test@example.com', 'password', 'failed', 'Invalid password');
echo "Test login attempt triggered. Check your email, Telegram, Slack, and alerts table.\n";
?>
