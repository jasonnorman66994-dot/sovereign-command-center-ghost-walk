# Health Check and Auto-Restart Script
# Checks harvester, engagement_monitor.ps1, and SMTP delivery service. Restarts and notifies via Telegram if any are down.

param(
    [string]$TelegramBotToken = "<YOUR_BOT_TOKEN>",
    [string]$ChatId = "<YOUR_CHAT_ID>"
)

function Send-TelegramAlert($msg) {
    $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage?chat_id=$ChatId&text=$msg"
    try { Invoke-RestMethod -Uri $url | Out-Null } catch {}
}

# 1. Check harvester (pm2)
$harvesterStatus = pm2 status harvester | Select-String "online"
if (-not $harvesterStatus) {
    pm2 restart harvester | Out-Null
    Send-TelegramAlert "[ALERT] Harvester was down. Auto-restarted at $(Get-Date)."
}

# 2. Check engagement_monitor.ps1 (process)
$engageProc = Get-Process -Name "pwsh" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*engagement_monitor.ps1*" }
if (-not $engageProc) {
    Start-Process pwsh -ArgumentList '-NoExit','-Command','.\engagement_monitor.ps1' | Out-Null
    Send-TelegramAlert "[ALERT] engagement_monitor.ps1 was not running. Relaunched at $(Get-Date)."
}

# 3. Check SMTP delivery (send_lures.ps1)
# (Assume it should be running if campaign is active. Add logic as needed.)

# 4. Schedule: Add to Task Scheduler or run in a loop for continuous monitoring.
# Example loop (uncomment to enable):
# while ($true) { .\health_check.ps1; Start-Sleep -Seconds 60 }
