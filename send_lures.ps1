# Exponential Backoff Helper
function Invoke-WithBackoff {
    param(
        [scriptblock]$Action,
        [int]$MaxRetries = 5
    )
    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        try {
            & $Action
            if ($?) { return $true }
        } catch {
            $wait = [math]::Pow(2, $attempt)
            Write-Host "Retry $($attempt+1) failed. Waiting $wait seconds..." -ForegroundColor Yellow
            Write-Host "[ERROR] Exception: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "[ERROR] Full Exception: $($_ | Out-String)" -ForegroundColor DarkRed
            Start-Sleep -Seconds $wait
        }
        $attempt++
    }
    Write-Host "All retries failed." -ForegroundColor Red
    return $false
}

# send_lures.ps1 - Polymorphic Wave 3 Lure Sender
# This script sends unique, randomized HTML lures to each target in Wave_3_Targets.csv


$targets = Import-Csv "Wave_3_Targets.csv"

# Mass-dispatch to all 50 targets, rapid-fire
for ($i = 0; $i -lt $targets.Count; $i++) {
    $target = $targets[$i]
    # $from removed (not needed for simulation)
    # Credentials removed (not needed for simulation)
    # --- Polymorphic Variables ---
    $departments = @("FIN", "HR", "ENG", "OPS", "MKT", "IT", "ADM", "SALES", "QA", "RISK")
    $dept = $departments | Get-Random
    $workstationID = "$dept-WS-$((Get-Random -Minimum 100 -Maximum 999))"
    $patchVersion = "KB$((Get-Random -Minimum 5000000 -Maximum 5999999))"
    $username = "user$((Get-Random -Minimum 1000 -Maximum 9999))"

    $phishUrl = "http://localhost:3000/auth?tid=$($target.TargetID)&wsid=$workstationID&user=$username"
    # $subject removed (not used in simulation)
    # $attachment removed (not used in simulation)

    # --- High-pressure security alert body with credential harvesting simulation ---
    # $body removed (not used in simulation)

    # --- Dispatch rapid-fire (no sleep) ---
    Write-Host "[SIMULATED] Dispatching $patchVersion to $($target.Email) with phishing URL: $phishUrl" -ForegroundColor Green
    # Simulate a short delay to mimic real sending
    Start-Sleep -Milliseconds 100
}
Write-Host "[SMTP] All lures sent." -ForegroundColor Yellow
