<?php
$pdo = new PDO('mysql:host=db;dbname=auth_db', 'authuser', 'authpass');
$devices = $pdo->query("SELECT device_fingerprint, user_id, MAX(timestamp) as last_seen, MAX(risk_score) as max_risk, COUNT(*) as login_count FROM auth_logs GROUP BY device_fingerprint, user_id ORDER BY max_risk DESC, last_seen DESC")->fetchAll();
?><!DOCTYPE html>
<html>
<head>
    <title>Device Risk Dashboard</title>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: #fff; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #444; }
        th { background: #333; }
        .high { background: #ff0000; }
        .medium { background: #ffcc00; color: #000; }
        .low { background: #00ff00; }
    </style>
</head>
<body>
    <h1>Device Risk Dashboard</h1>
    <table>
        <tr>
            <th>Device Fingerprint</th>
            <th>User ID</th>
            <th>Last Seen</th>
            <th>Max Risk</th>
            <th>Login Count</th>
        </tr>
        <?php foreach($devices as $device):
            $risk_class = $device['max_risk'] >= 10 ? 'high' : ($device['max_risk'] >= 5 ? 'medium' : 'low');
        ?>
        <tr class="<?php echo $risk_class; ?>">
            <td><?php echo htmlspecialchars($device['device_fingerprint']); ?></td>
            <td><?php echo htmlspecialchars($device['user_id']); ?></td>
            <td><?php echo htmlspecialchars($device['last_seen']); ?></td>
            <td><?php echo htmlspecialchars($device['max_risk']); ?></td>
            <td><?php echo htmlspecialchars($device['login_count']); ?></td>
        </tr>
        <?php endforeach; ?>
    </table>
</body>
</html>
