# --- CONFIGURATION ---

# --- CONFIGURATION ---
$dbPath = ".\harvester_data.db"
$snapshotDir = ".\board_snapshots"
$sqlitePath = "C:\Users\HomePC\Downloads\sqlite-tools-win-x64-3530000\sqlite3.exe"

if (!(Test-Path $snapshotDir)) { New-Item -ItemType Directory -Path $snapshotDir }

# --- FUNCTION: BOARDROOM KPI SNAPSHOT ---

# --- FUNCTION: BOARDROOM KPI SNAPSHOT ---
function New-BoardroomSnapshot {
    # Ensure your Get-CampaignMetrics function is defined in your profile or this script
    $metrics = Get-CampaignMetrics 
    $timestamp = Get-Date -Format "yyyyMMdd_HHmm"
    $filename = "Engagement_Snapshot_$timestamp.csv"
    
    $metrics | Export-Csv -Path "$snapshotDir\$filename" -NoTypeInformation
    Write-Host "`n[+] Boardroom Snapshot Locked: $filename" -ForegroundColor Green
    Write-Host "[+] Data saved to $snapshotDir" -ForegroundColor Gray
}

# --- MAIN MONITORING LOOP ---

# --- MAIN MONITORING LOOP ---
Write-Host "--- Adversarial Command Center: Active ---" -ForegroundColor Cyan
Write-Host "[i] Monitoring for Scanner Activity..." -ForegroundColor Gray

while($true) {
    # Check for Scanner hits in the last 2 minutes
    $scanQuery = "SELECT COUNT(*) FROM telemetry WHERE event_type = 'Scanner_Hit' AND timestamp > datetime('now', '-2 minutes')"
    $scanDetected = & $sqlitePath $dbPath $scanQuery
    
    if ([int]$scanDetected -gt 0) {
        Write-Host "`n[!] ALERT: Scanner Activity Detected at $(Get-Date)" -ForegroundColor Red
        Write-Host "[!] Action Required: Evaluate domain rotation in config.json." -ForegroundColor Yellow
        
        # Trigger notification if BurntToast is installed
        try { New-BurntToastNotification -Text "PIVOT REQUIRED", "Security scanners are probing the infrastructure." } catch {}
    }

    Write-Host "." -NoNewline
    Start-Sleep -Seconds 60
}
