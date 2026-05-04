# Heartbeat/Dead Man's Snitch Script
# Schedule this script to run every 60 minutes via Task Scheduler


# Hardened Dead Man's Snitch (heartbeat.ps1)
$NodeService = "YourNodeService"  # Replace with your actual Node.js service name
$PowerShellService = "YourPowerShellService"  # Replace if needed
$TelegramBotToken = "<YOUR_BOT_TOKEN>"
$TelegramChatId = "<YOUR_CHAT_ID>"
$HealthUrl = "http://localhost:3000/health"  # Your Node.js health endpoint
$LogFile = "C:\Scripts\snitch.log"  # Adjust path as needed
$HeartbeatMsg = "Heartbeat: Sovereign Command Center is alive. $(Get-Date -Format 'u')"
$AlertMsg = "Critical: Service Restarted at $(Get-Date -Format 'u')"

function Write-Log($msg) {
    Add-Content -Path $LogFile -Value ("[$(Get-Date -Format 'u')] $msg")
}

function Send-TelegramMessage($msg) {
    $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage"
    try {
        Invoke-RestMethod -Uri $url -Method Post -Body @{ chat_id = $TelegramChatId; text = $msg } -TimeoutSec 10
    } catch {
        Write-Log "[ERROR] Failed to send Telegram message: $msg"
    }
}

$healthy = $false
try {
    $apiCheck = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 10
    if ($apiCheck.StatusCode -eq 200) {
        $healthy = $true
    } else {
        throw "API returned status $($apiCheck.StatusCode)"
    }
} catch {
    Write-Log "[WARN] Health check failed: $_"
}

if ($healthy) {
    Send-TelegramMessage $HeartbeatMsg
    Write-Log "Heartbeat sent."
} else {
    Restart-Service -Name $NodeService -Force -ErrorAction SilentlyContinue
    Restart-Service -Name $PowerShellService -Force -ErrorAction SilentlyContinue
    Send-TelegramMessage $AlertMsg
    Write-Log "Critical: Service(s) restarted and alert sent."
}
