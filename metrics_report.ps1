# Metrics Reporting Script
# Extracts campaign metrics and sends a summary to Telegram.

param(
    [string]$TelegramBotToken = "<YOUR_BOT_TOKEN>",
    [string]$ChatId = "<YOUR_CHAT_ID>"
)

function Send-TelegramAlert($msg) {
    $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage?chat_id=$ChatId&text=$msg"
    try { Invoke-RestMethod -Uri $url | Out-Null } catch {}
}

# Example: Extract metrics from SQLite (adjust as needed)
$sqlitePath = "C:\\Users\\HomePC\\Downloads\\sqlite-tools-win-x64-3530000\\sqlite3.exe"
$dbPath = ".\\harvester_data.db"

# Total credentials harvested
$totalHarvest = & $sqlitePath $dbPath "SELECT COUNT(*) FROM telemetry WHERE event_type = 'Credential_Harvest'"
# Unique targets
$uniqueTargets = & $sqlitePath $dbPath "SELECT COUNT(DISTINCT email) FROM telemetry WHERE event_type = 'Credential_Harvest'"
# Mean Time to Detection (MTTD)
$mttd = & $sqlitePath $dbPath "SELECT AVG(julianday(timestamp) - julianday((SELECT MIN(timestamp) FROM telemetry))) * 24 * 60 FROM telemetry WHERE event_type = 'Credential_Harvest'"

$msg = "[METRICS REPORT]\nTotal Harvested: $totalHarvest\nUnique Targets: $uniqueTargets\nMTTD (min): $([math]::Round($mttd,2))"
Send-TelegramAlert $msg

# Schedule this script for daily/weekly reporting.
