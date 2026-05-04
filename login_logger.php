<?php
// login_logger.php - Add this to your login handler
/**
 * Log an authentication attempt
 * @param string $user_id
 * @param string $email
 * @param string $method
 * @param string $result
 * @param string|null $failure_reason
 */
function logAuthAttempt($user_id, $email, $method, $result, $failure_reason = null) {
    global $pdo; // your database connection
    $ip = $_SERVER['REMOTE_ADDR'];
    $geo = getGeoLocation($ip); // use service like ipapi.co
    $fingerprint = md5(
        $_SERVER['HTTP_USER_AGENT'] . 
        $_SERVER['HTTP_ACCEPT_LANGUAGE'] . 
        $_SERVER['HTTP_ACCEPT_ENCODING']
    );
    $allowed_countries = ['USA', 'Canada'];
    $risk = 0;
    if ($result === 'failed') $risk += 5;
    if ($method === 'password') $risk += 2;
    // Rate limiting: max 3 alerts per user/IP per hour
    $rateLimitStmt = $pdo->prepare("SELECT COUNT(*) FROM alerts WHERE user_id = ? AND ip_address = ? AND alert_time > datetime('now', '-1 hour')");
    $rateLimitStmt->execute([$user_id, $ip]);
    $alertCount = $rateLimitStmt->fetchColumn();
    $alert_triggered = false;
    if (!in_array(($geo['country'] ?? 'Unknown'), $allowed_countries)) {
        $risk += 20;
        if ($alertCount < 3) {
            $alert_triggered = true;
            $alert_subject = 'Geo-fence Alert: ' . ($geo['country'] ?? 'Unknown');
            $alert_body = "ALERT: Blocked login from " . ($geo['country'] ?? 'Unknown') . "\n"
                . "User: $user_id ($email)\n"
                . "IP: $ip\n"
                . "City: " . ($geo['city'] ?? 'Unknown') . "\n"
                . "Lat/Lon: " . ($geo['latitude'] ?? 'N/A') . ", " . ($geo['longitude'] ?? 'N/A') . "\n"
                . "User Agent: " . $_SERVER['HTTP_USER_AGENT'] . "\n"
                . "Method: $method\n"
                . "Result: $result\n"
                . "Failure Reason: $failure_reason\n"
                . "Risk Score: $risk\n"
                . "Time: " . date('c') . "\n";
            // Email alert
            $alert_sent = mail(
                'security@yourcompany.com',
                $alert_subject,
                $alert_body,
                "From: noreply@yourcompany.com\r\n"
            );
            // Telegram alert (optional, fill in your bot token and chat ID)
            $telegramResult = sendTelegramAlert($alert_body);
            // Slack alert (optional, fill in your webhook URL)
            $slackResult = sendSlackAlert($alert_body);
            // Log alert to alerts table
            $alertLogStmt = $pdo->prepare("INSERT INTO alerts (user_id, email, ip_address, country, city, latitude, longitude, user_agent, method, result, failure_reason, risk_score, alert_time, alert_channel, telegram_status, slack_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
            $alertLogStmt->execute([
                $user_id,
                $email,
                $ip,
                $geo['country'] ?? 'Unknown',
                $geo['city'] ?? 'Unknown',
                $geo['latitude'] ?? null,
                $geo['longitude'] ?? null,
                $_SERVER['HTTP_USER_AGENT'],
                $method,
                $result,
                $failure_reason,
                $risk,
                date('Y-m-d H:i:s'),
                'email,telegram,slack',
                $telegramResult,
                $slackResult
            ]);
            if ($alert_sent) {
                error_log("[ALERT] Geo-fence alert sent for user $user_id ($email) from IP $ip");
            } else {
                error_log("[ALERT] Geo-fence alert FAILED for user $user_id ($email) from IP $ip");
            }
        // Slack alert integration (fill in your webhook URL)
        /**
         * Send a Slack alert
         * @param string $message
         * @return string
         */
        function sendSlackAlert($message) {
            $webhookUrl = 'YOUR_SLACK_WEBHOOK_URL'; // <-- Replace with your Slack webhook URL
            if ($webhookUrl === 'YOUR_SLACK_WEBHOOK_URL') {
                return 'not_configured';
            }
            $payload = json_encode(["text" => $message]);
            $options = [
                'http' => [
                    'header'  => "Content-type: application/json\r\n",
                    'method'  => 'POST',
                    'content' => $payload,
                    'timeout' => 5
                ]
            ];
            $context  = stream_context_create($options);
            $result = @file_get_contents($webhookUrl, false, $context);
            if ($result === FALSE) {
                return 'failed';
            }
            return 'sent';
        }
        } else {
            error_log("[ALERT] Rate limit reached for user $user_id ($email) from IP $ip");
        }
    }
    // Add more rules as needed
    $stmt = $pdo->prepare("
        INSERT INTO auth_logs (
            user_id, email, ip_address, user_agent, method, result, 
            failure_reason, country, city, latitude, longitude, 
            device_fingerprint, session_id, risk_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");
    $stmt->execute([
        $user_id,
        $email,
        $ip,
        $_SERVER['HTTP_USER_AGENT'],
        $method,
        $result,
        $failure_reason,
        $geo['country'] ?? 'Unknown',
        $geo['city'] ?? 'Unknown',
        $geo['latitude'] ?? null,
        $geo['longitude'] ?? null,
        $fingerprint,
        session_id(),
        $risk
    ]);
}

// Telegram alert integration (fill in your bot token and chat ID)
/**
 * @param string $message
 */
function sendTelegramAlert(string $message) {
    $botToken = 'YOUR_TELEGRAM_BOT_TOKEN'; // <-- Replace with your bot token
    $chatId = 'YOUR_TELEGRAM_CHAT_ID';     // <-- Replace with your chat ID
    if ($botToken === 'YOUR_TELEGRAM_BOT_TOKEN' || $chatId === 'YOUR_TELEGRAM_CHAT_ID') {
        return 'not_configured';
    }
    $url = "https://api.telegram.org/bot$botToken/sendMessage";
    $data = [
        'chat_id' => $chatId,
        'text' => $message
    ];
    $options = [
        'http' => [
            'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
            'method'  => 'POST',
            'content' => http_build_query($data),
            'timeout' => 5
        ]
    ];
    $context  = stream_context_create($options);
    $result = @file_get_contents($url, false, $context);
    if ($result === FALSE) {
        return 'failed';
    }
    return 'sent';
}
/**
 * @param string $ip
 */
function getGeoLocation(string $ip) {
    $response = @file_get_contents("https://ipapi.co/{$ip}/json/");
    if ($response === FALSE) return [];
    return json_decode($response, true);
}
?>