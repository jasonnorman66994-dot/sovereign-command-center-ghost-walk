
# --- AUTOMATED CAMPAIGN ORCHESTRATION SCRIPT ---
# Now includes:
# 1. Telegram handshake test and CHAT_ID confirmation
# 2. pm2 restart for all Node.js/PowerShell services
# 3. Launch engagement_monitor.ps1 in new terminal
# 4. Execute SMTP delivery script with jitter
# 5. Schedule New-BoardroomSnapshot after 30 minutes

param(
    [int]$Phases = 5,
    [int]$LuresPerPhase = 20,
    [int]$JitterMin = 10,
    [int]$JitterMax = 40,
    [int]$IntervalBetweenPhases = 1800, # 30 minutes
    [switch]$SnapshotAfterPhase
)

# 1. Telegram handshake test
Write-Host "[AUTOMATION] Verifying Telegram handshake and CHAT_ID..." -ForegroundColor Cyan
pwsh -File .\verify_telegram.ps1

# 2. pm2 restart all services
Write-Host "[AUTOMATION] Restarting all pm2 services..." -ForegroundColor Cyan
pm2 restart all | Out-Null

# 3. Launch engagement_monitor.ps1 in new terminal
Write-Host "[AUTOMATION] Launching engagement_monitor.ps1 in new terminal..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList '-NoExit','-Command','.\engagement_monitor.ps1' | Out-Null

for ($phase = 1; $phase -le $Phases; $phase++) {
    Write-Host ("[CAMPAIGN] Launching Phase {0}..." -f $phase) -ForegroundColor Cyan
    # 4. Execute SMTP delivery script with jitter
    pwsh -File .\send_lures.ps1 -Limit $LuresPerPhase -JitterMin $JitterMin -JitterMax $JitterMax
    Write-Host ("[CAMPAIGN] Phase {0} complete. Waiting {1} seconds before next phase..." -f $phase, $IntervalBetweenPhases) -ForegroundColor Yellow
    if ($SnapshotAfterPhase) {
        Write-Host "[CAMPAIGN] Triggering boardroom snapshot..." -ForegroundColor Green
        pwsh -Command ".\engagement_monitor.ps1 -Snapshot"
    }
    if ($phase -lt $Phases) {
        Start-Sleep -Seconds $IntervalBetweenPhases
    }
}

# 5. Schedule New-BoardroomSnapshot after 30 minutes (if not already triggered)
if (-not $SnapshotAfterPhase) {
    Write-Host "[AUTOMATION] Scheduling New-BoardroomSnapshot in 30 minutes..." -ForegroundColor Cyan
    Start-Job -ScriptBlock {
        Start-Sleep -Seconds 1800
        pwsh -Command ".\engagement_monitor.ps1 -Snapshot"
    } | Out-Null
}

Write-Host "[CAMPAIGN] All phases complete. Monitoring for detections..." -ForegroundColor Magenta
