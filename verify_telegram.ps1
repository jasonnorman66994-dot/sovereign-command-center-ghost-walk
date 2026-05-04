# --- CONFIG ---
$botToken = "8486086452:AAFB2NUlC4Mc58tT0AXpX8FM7dMFMm-26pM"

# --- ACTION: FETCH CHAT ID 8486086452---
Write-Host "[*] Fetching latest Telegram updates..." -ForegroundColor Cyan
$url = "https://api.telegram.org/bot$botToken/getUpdates"
$response = Invoke-RestMethod -Uri $url

if ($response.result.count -gt 0) {
    $chatId = $response.result[-1].message.chat.id
    $username = $response.result[-1].message.chat.username
    Write-Host "[+] Found Chat ID: $chatId (User: @$username)" -ForegroundColor Green
    
    # Send Test Message
    $testUrl = "https://api.telegram.org/bot$botToken/sendMessage?chat_id=$chatId&text=Handshake Verified. Operational Command Center Online."
    Invoke-RestMethod -Uri $testUrl | Out-Null
    Write-Host "[+] Handshake message sent to your phone." -ForegroundColor Gray
} else {
    Write-Host "[!] No messages found. Please send a message to my bot on Telegram first!" -ForegroundColor Red
}
