<?php
// Passwordless login: send magic link or OTP
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'];
    $otp = rand(100000, 999999);
    // Store OTP in DB (email_auth_logs)
    $pdo = new PDO('mysql:host=db;dbname=auth_db', 'authuser', 'authpass');
    $stmt = $pdo->prepare("INSERT INTO email_auth_logs (email, auth_type, code, request_ip, request_location, expires_at) VALUES (?, 'magic', ?, ?, ?, NOW() + INTERVAL 10 MINUTE)");
    $stmt->execute([$email, $otp, $_SERVER['REMOTE_ADDR'], 'Unknown']);
    // Send OTP via email (use mail() or SMTP)
    mail($email, 'Your Login Code', "Your login code is: $otp");
    echo 'OTP sent!';
    exit;
}
?>
<form method="POST">
    <input type="email" name="email" placeholder="Enter your email" required />
    <button type="submit">Send Magic Link / OTP</button>
</form>
