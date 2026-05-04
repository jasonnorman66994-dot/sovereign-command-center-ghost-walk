# PowerShell orchestrator for full GeoIP enrichment and reporting pipeline
# Usage: .\geoip_enrich.ps1

# --- CONFIG ---
$sqlitePath = "C:/Users/HomePC/Downloads/sqlite-tools-win-x64-3530000/sqlite3.exe"
$dbPath = ".\\harvester_data.db"
$IpList = "ip_list.txt"
$Output = "geoip_results.csv"
$pythonExe = "python"
$geoipScript = "batch_geoip.py"
$reportScript = "daily_report.ps1"
# List of high-risk countries (ISO codes)
$highRiskCountries = @("RU", "CN", "KP", "IR", "SY")
# Telegram notification config (update as needed)
# Telegram notification config
$TelegramBotToken = "8486086452:AAFB2NUlC4Mc58tT0AXpX8FM7dMFMm-26pM"
$ChatId = "8485160683"
# Slack webhook — set via SLACK_WEBHOOK_URL environment variable
$SlackWebhook = $env:SLACK_WEBHOOK_URL

# --- 1. Extract IPs from telemetry ---
Write-Host "[GeoIP] Extracting IPs from telemetry..." -ForegroundColor Cyan
& $sqlitePath $dbPath "SELECT DISTINCT ip FROM telemetry WHERE ip IS NOT NULL AND ip != ''" | Set-Content $IpList

# --- 2. Run the Python batch enrichment ---
Write-Host "[GeoIP] Enriching IPs from $IpList ..." -ForegroundColor Cyan
$cmd = "$pythonExe $geoipScript $IpList $Output"
Invoke-Expression $cmd

# --- 3. Custom notifications for high-risk IPs ---
if (Test-Path $Output) {
    Write-Host "[GeoIP] Results written to $Output" -ForegroundColor Green
    $geoipData = Import-Csv $Output
    $risky = $geoipData | Where-Object { $highRiskCountries -contains $_.country_iso }

    if ($risky) {
        $msg = "[ALERT] High-risk IPs detected: " + ($risky | ForEach-Object { $_.ip + " (" + $_.country_iso + ")" }) -join ", "
        Write-Host $msg -ForegroundColor Red
        # Telegram alert
        if ($TelegramBotToken -and $ChatId -and $msg.Length -lt 4000) {
            $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage?chat_id=$ChatId&text=$([uri]::EscapeDataString($msg))"
            try { Invoke-RestMethod -Uri $url | Out-Null } catch {}
        }
        # Slack alert
        if ($SlackWebhook -and $SlackWebhook -ne "") {
            $payload = @{ text = $msg } | ConvertTo-Json
            try { Invoke-RestMethod -Uri $SlackWebhook -Method Post -Body $payload -ContentType 'application/json' | Out-Null } catch {}
        }
        # --- Custom logic hook: add more alert channels or actions here ---
        # Example: Email, Teams, SMS, etc.
    }

    # --- 4. Connect to reporting pipeline (attach to daily report) ---
    if (Test-Path $reportScript) {
        Write-Host "[GeoIP] Attaching $Output to daily report..." -ForegroundColor Cyan
        pwsh -File $reportScript -ExtraAttachments @($Output)
    } else {
        Write-Host "[GeoIP] daily_report.ps1 not found, skipping report integration." -ForegroundColor Yellow
    }
} else {
    Write-Host "[GeoIP] Failed to write results." -ForegroundColor Red
}
