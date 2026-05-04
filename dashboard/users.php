<?php
$pdo = new PDO('mysql:host=db;dbname=auth_db', 'authuser', 'authpass');
$users = $pdo->query("SELECT user_id, email, MAX(timestamp) as last_seen, MAX(risk_score) as max_risk, COUNT(*) as login_count FROM auth_logs GROUP BY user_id, email ORDER BY max_risk DESC, last_seen DESC")->fetchAll();
?><!DOCTYPE html>
<html>
<head>
    <title>User Risk Dashboard</title>
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
    <h1>User Risk Dashboard</h1>
    <table>
        <tr>
            <th>User ID</th>
            <th>Email</th>
            <th>Last Seen</th>
            <th>Max Risk</th>
            <th>Login Count</th>
        </tr>
        <?php foreach($users as $user):
            $risk_class = $user['max_risk'] >= 10 ? 'high' : ($user['max_risk'] >= 5 ? 'medium' : 'low');
        ?>
        <tr class="<?php echo $risk_class; ?>">
            <td><?php echo htmlspecialchars($user['user_id']); ?></td>
            <td><?php echo htmlspecialchars($user['email']); ?></td>
            <td><?php echo htmlspecialchars($user['last_seen']); ?></td>
            <td><?php echo htmlspecialchars($user['max_risk']); ?></td>
            <td><?php echo htmlspecialchars($user['login_count']); ?></td>
        </tr>
        <?php endforeach; ?>
    </table>
</body>
</html>
