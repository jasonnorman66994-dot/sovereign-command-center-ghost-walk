<?php
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
?>
<div class="metric">
    <h3>Logins (5 min)</h3>
    <p><?php echo $metrics['logins_5min']; ?></p>
</div>
<div class="metric <?php echo $metrics['failed_5min'] > 10 ? 'alert critical' : ''; ?>">
    <h3>Failed Logins (5 min)</h3>
    <p><?php echo $metrics['failed_5min']; ?></p>
</div>
<div class="metric">
    <h3>Unique IPs (5 min)</h3>
    <p><?php echo $metrics['unique_ips']; ?></p>
</div>
<div class="metric">
    <h3>Countries (5 min)</h3>
    <p><?php echo $metrics['countries']; ?></p>
</div>
<div class="metric">
    <h3>Active Tokens</h3>
    <p><?php echo $metrics['active_tokens']; ?></p>
</div>
<div class="metric">
    <h3>Active Cookies</h3>
    <p><?php echo $metrics['active_cookies']; ?></p>
</div>
<div class="metric <?php echo $metrics['unresolved_alerts'] > 0 ? 'alert critical' : ''; ?>">
    <h3>🚨 Alerts</h3>
    <p><?php echo $metrics['unresolved_alerts']; ?></p>
</div>
