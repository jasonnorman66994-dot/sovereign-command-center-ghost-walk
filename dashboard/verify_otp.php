<?php
// Verify OTP for passwordless login
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'];
    $otp = $_POST['otp'];
    $pdo = new PDO('mysql:host=db;dbname=auth_db', 'authuser', 'authpass');
    $stmt = $pdo->prepare("SELECT * FROM email_auth_logs WHERE email = ? AND code = ? AND used = FALSE AND expires_at > NOW()");
    $stmt->execute([$email, $otp]);
    $row = $stmt->fetch();
    if ($row) {
        // Mark OTP as used
        $pdo->prepare("UPDATE email_auth_logs SET used = TRUE, used_at = NOW() WHERE id = ?")->execute([$row['id']]);
        echo 'Login successful!';
        // Set session/cookie as needed
    } else {
        echo 'Invalid or expired code.';
    }
    exit;
}
?>
<form method="POST">
    <input type="email" name="email" placeholder="Enter your email" required />
    <input type="text" name="otp" placeholder="Enter OTP" required />
    <button type="submit">Verify</button>
</form>
