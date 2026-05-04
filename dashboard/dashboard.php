<?php
// dashboard.php - Live Security Dashboard
$pdo = new PDO('mysql:host=db;dbname=auth_db', 'authuser', 'authpass');
$metrics = $pdo->query("
    SELECT 
        (SELECT COUNT(*) FROM auth_logs WHERE timestamp >= NOW() - INTERVAL 5 MINUTE) as logins_5min,
        (SELECT COUNT(*) FROM auth_logs WHERE result = 'failed' AND timestamp >= NOW() - INTERVAL 5 MINUTE) as failed_5min,
        (SELECT COUNT(DISTINCT ip_address) FROM auth_logs WHERE timestamp >= NOW() - INTERVAL 5 MINUTE) as unique_ips,
        (SELECT COUNT(DISTINCT country) FROM auth_logs WHERE timestamp >= NOW() - INTERVAL 5 MINUTE) as countries,
        (SELECT COUNT(*) FROM token_logs WHERE is_active = TRUE AND expires_at > NOW()) as active_tokens,
        (SELECT COUNT(*) FROM cookie_logs WHERE is_active = TRUE AND expires_at > NOW()) as active_cookies,
        (SELECT COUNT(*) FROM security_alerts WHERE resolved = FALSE) as unresolved_alerts
")->fetch();
?><!DOCTYPE html>
<html>
<head>
    <title>Live Security Dashboard</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
    function refreshMetrics() {
        $.get('metrics.php', function(data) {
            $('#metrics').html(data);
        });
    }
    setInterval(refreshMetrics, 5000); // 5 seconds
    $(document).ready(refreshMetrics);
    </script>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px; }
        .metric { background: #2a2a2a; padding: 20px; margin: 10px; border-radius: 8px; display: inline-block; min-width: 200px; }
        .metric h3 { margin: 0; color: #00ff00; }
        .metric p { font-size: 32px; margin: 10px 0; }
        .critical { background: #ff0000; }
        .high { background: #ff6600; }
        .medium { background: #ffcc00; color: #000; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #444; }
        th { background: #333; }
        .alert { animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>
    <h1>🔒 Live Security Monitoring Dashboard</h1>
    <p>Live updates every 5 seconds</p>
    <div id="metrics"></div>
    <h2>Recent Activity (Last 10 Logins)</h2>
    <table>
        <tr>
            <th>Time</th>
            <th>User</th>
            <th>Method</th>
            <th>Result</th>
            <th>IP</th>
            <th>Location</th>
        </tr>
        <?php
        $recent = $pdo->query("
            SELECT timestamp, email, method, result, ip_address, CONCAT(city, ', ', country) as location
            FROM auth_logs 
            ORDER BY timestamp DESC 
            LIMIT 10
        ");
        while($row = $recent->fetch()) {
            $class = $row['result'] == 'failed' ? 'class="alert"' : '';
            echo "<tr $class>";
            echo "<td>{$row['timestamp']}</td>";
            echo "<td>{$row['email']}</td>";
            echo "<td>{$row['method']}</td>";
            echo "<td>{$row['result']}</td>";
            echo "<td>{$row['ip_address']}</td>";
            echo "<td>{$row['location']}</td>";
            echo "</tr>";
        }
        ?>
    </table>
    <h2>🔥 Active Alerts</h2>
    <table>
        <tr>
            <th>Time</th>
            <th>Type</th>
            <th>Severity</th>
            <th>User</th>
            <th>IP</th>
            <th>Description</th>
        </tr>
        <?php
        $alerts = $pdo->query("
            SELECT * FROM security_alerts 
            WHERE resolved = FALSE 
            ORDER BY timestamp DESC
        ");
        while($row = $alerts->fetch()) {
            $severity_class = strtolower($row['severity']);
            echo "<tr class='$severity_class'>";
            echo "<td>{$row['timestamp']}</td>";
            echo "<td>{$row['alert_type']}</td>";
            echo "<td>{$row['severity']}</td>";
            echo "<td>{$row['user_id']}</td>";
            echo "<td>{$row['ip_address']}</td>";
            echo "<td>{$row['description']}</td>";
            echo "</tr>";
        }
        ?>
    </table>
    <h2>🍪 Cookie Activity (Last Hour)</h2>
    <table>
        <tr>
            <th>Cookie ID</th>
            <th>User</th>
            <th>Last IP</th>
            <th>Location</th>
            <th>Last Seen</th>
            <th>Expires</th>
            <th>Status</th>
        </tr>
        <?php
        $cookies = $pdo->query("
            SELECT cookie_id, user_id, last_seen_ip, last_seen_location, 
                   last_seen_at, expires_at, is_active
            FROM cookie_logs 
            WHERE last_seen_at >= NOW() - INTERVAL 1 HOUR
            ORDER BY last_seen_at DESC
            LIMIT 20
        ");
        while($row = $cookies->fetch()) {
            $status = $row['is_active'] ? '✅ Active' : '❌ Revoked';
            echo "<tr>";
            echo "<td>" . substr($row['cookie_id'], 0, 12) . "...</td>";
            echo "<td>{$row['user_id']}</td>";
            echo "<td>{$row['last_seen_ip']}</td>";
            echo "<td>{$row['last_seen_location']}</td>";
            echo "<td>{$row['last_seen_at']}</td>";
            echo "<td>{$row['expires_at']}</td>";
            echo "<td>$status</td>";
            echo "</tr>";
        }
        ?>
    </table>
</body>
</html>
