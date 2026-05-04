<?php
// Email MFA: send and verify code
session_start();
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'];
    $action = $_POST['action'] ?? '';
    $pdo = new PDO('mysql:host=db;dbname=auth_db', 'authuser', 'authpass');
    if ($action === 'send') {
        $code = rand(100000, 999999);
        $stmt = $pdo->prepare("INSERT INTO email_auth_logs (email, auth_type, code, request_ip, request_location, expires_at) VALUES (?, 'mfa', ?, ?, ?, NOW() + INTERVAL 10 MINUTE)");
        $stmt->execute([$email, $code, $_SERVER['REMOTE_ADDR'], 'Unknown']);
        mail($email, 'Your MFA Code', "Your MFA code is: $code");
        $_SESSION['mfa_email'] = $email;
        echo 'MFA code sent!';
        exit;
    } elseif ($action === 'verify') {
        $code = $_POST['code'];
        $stmt = $pdo->prepare("SELECT * FROM email_auth_logs WHERE email = ? AND code = ? AND auth_type = 'mfa' AND used = FALSE AND expires_at > NOW()");
        $stmt->execute([$email, $code]);
        $row = $stmt->fetch();
        if ($row) {
            $pdo->prepare("UPDATE email_auth_logs SET used = TRUE, used_at = NOW() WHERE id = ?")->execute([$row['id']]);
            echo 'MFA verified!';
        } else {
            echo 'Invalid or expired code.';
        }
        exit;
    }
}
?>
<form method="POST">
    <input type="email" name="email" placeholder="Enter your email" required />
    <button type="submit" name="action" value="send">Send MFA Code</button>
</form>
<form method="POST">
    <input type="email" name="email" placeholder="Enter your email" required />
    <input type="text" name="code" placeholder="Enter MFA code" required />
    <button type="submit" name="action" value="verify">Verify MFA</button>
</form>