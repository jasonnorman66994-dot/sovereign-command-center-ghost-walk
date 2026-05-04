# PowerShell script to create a phishing simulation alert JSON and start the response timer

param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    [Parameter(Mandatory=$true)]
    [string]$RemoteAddress,
    [Parameter(Mandatory=$true)]
    [string]$LandingUrl,
    [Parameter(Mandatory=$true)]
    [string]$UserAgent,
    [Parameter(Mandatory=$true)]
    [string]$HeadersFile # Path to a file containing raw headers (optional for enrichment)
)

$timestamp = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssZ')
$alert = [ordered]@{
    alertType    = 'PHISHING SIMULATION: Credential Entry'
    severity     = 'HIGH'
    username     = $Username
    remoteAddress= $RemoteAddress
    landingUrl   = $LandingUrl
    userAgent    = $UserAgent
    timestamp    = $timestamp
    isSimulation = $true
    description  = 'User clicked simulation link and provided credentials on a non-corporate domain.'
    headers      = if (Test-Path $HeadersFile) { Get-Content $HeadersFile -Raw } else { $null }
}

# Save alert JSON
$alertFile = "alert_${Username.Replace('@','_').Replace('.','_')}_phishingsim_$(Get-Date -Format yyyyMMdd_HHmmss).json"
$alert | ConvertTo-Json -Depth 10 | Set-Content $alertFile

# Start the response timer (sim_tracking)
$simDir = "sim_tracking"
if (!(Test-Path $simDir)) { New-Item -ItemType Directory -Path $simDir | Out-Null }
Set-Content -Path "$simDir/$Username.txt" -Value (Get-Date)

Write-Host "Phishing simulation alert created: $alertFile"
