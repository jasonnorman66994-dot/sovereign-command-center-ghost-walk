
# --- CONFIG ---
$targetFile = ".\targets.csv"  # Ensure my 15-20 targets are here
$smtpScript = ".\send_lures.ps1" # Your existing delivery logic
$maxInitialSends = 20

Write-Host "--- Phase 1: Operational Launch Initiated ---" -ForegroundColor Cyan
Write-Host "[!] Target Count: $maxInitialSends" -ForegroundColor Gray
Write-Host "[!] Jitter Profile: 10s - 40s (Stealth Mode)" -ForegroundColor Gray

# --- EXECUTION ---
try {
    # This calls my delivery script for the first 20 targets
    & $smtpScript -TargetFile $targetFile -Limit $maxInitialSends -JitterMin 10 -JitterMax 40
    
    Write-Host "`n[+] Wave 1 Complete. SMTP Thread Idle." -ForegroundColor Green
    Write-Host "[*] MISSION: Monitoring for Mean Time to Detection (MTTD)." -ForegroundColor Yellow
} catch {
    Write-Host "[!] Launch Error: $($_.Exception.Message)" -ForegroundColor Red
}

# --- POST-LAUNCH INSTRUCTIONS ---
Write-Host "`nNEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Keep 'engagement_monitor.ps1' running in my side terminal."
Write-Host "2. Watch my phone for Telegram alerts (Red Pulses)."
Write-Host "3. After 60 minutes, run: New-BoardroomSnapshot"
