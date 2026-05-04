# snitchLogMonitor.ps1
# Run every 12 hours (Task Scheduler)
# If >3 restarts in last 12h, send alert with last 10 lines of snitch.log

$LogFile = "C:\Scripts\snitch.log"
$TelegramBotToken = "<YOUR_BOT_TOKEN>"
$TelegramChatId = "<YOUR_CHAT_ID>"
$RestartCount = (Get-Content $LogFile | Select-String -Pattern "Service Restarted" | Where-Object { $_.Line -match (Get-Date).AddHours(-12).ToString("yyyy-MM-dd") } | Measure-Object).Count

if ($RestartCount -gt 3) {
    $last10 = Get-Content $LogFile | Select-Object -Last 10 | Out-String
    $msg = "System Instability: $RestartCount restarts in last 12h.\nLast 10 log lines:\n$last10"
    $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage"
    Invoke-RestMethod -Uri $url -Method Post -Body @{ chat_id = $TelegramChatId; text = $msg }
}
