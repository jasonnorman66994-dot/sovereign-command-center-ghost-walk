# Log Rotation Script
# Rotates snitch.log and alert_automation.log daily or if size > 5MB. Compresses and archives old logs.


# --- CONFIG ---
$logFiles = @(".\snitch.log", ".\alert_automation.log")
$archiveDir = ".\log_archive"
$maxSizeMB = 5
$TelegramBotToken = "<YOUR_BOT_TOKEN>"
$ChatId = "<YOUR_CHAT_ID>"

function Send-TelegramAlert($msg) {
    $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage?chat_id=$ChatId&text=$msg"
    try { Invoke-RestMethod -Uri $url | Out-Null } catch {}
}

if (!(Test-Path $archiveDir)) { New-Item -ItemType Directory -Path $archiveDir | Out-Null }

foreach ($log in $logFiles) {
    if (Test-Path $log) {
        $sizeMB = (Get-Item $log).Length / 1MB
        $date = Get-Date -Format "yyyyMMdd_HHmm"
        $archiveName = "{0}_{1}.log" -f ([IO.Path]::GetFileNameWithoutExtension($log)), $date
        $archivePath = Join-Path $archiveDir $archiveName
        if ($sizeMB -ge $maxSizeMB -or (Get-Date).Hour -eq 0) {
            Move-Item $log $archivePath
            Compress-Archive -Path $archivePath -DestinationPath "$archivePath.zip"
            Remove-Item $archivePath
            New-Item -ItemType File -Path $log | Out-Null
            Send-TelegramAlert "[LOG ROTATION] $log rotated and archived at $date."
        }
    }
}

# Schedule this script with Task Scheduler for daily or hourly execution.
