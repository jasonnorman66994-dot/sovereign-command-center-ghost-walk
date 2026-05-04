# Mock Data for Simulation
$simData = @{
    username      = "sjones@alphamechanical.com"
    password      = "GuL11156"
    landingUrl    = "https://login.kinonlisplazmaoplayer.xyz/JmzQ7F90IQ2DKzW"
    userAgent     = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1"
    remoteAddress = "2600:1700:84b0:1120:510b:9c9c:6f4e:1a2b"
    customType    = "Credential_Harvest"
    extraContext  = "eyJhY2Nlc3NfdG9rZW4iOiAiWkdWMmJXbHVhVzVuSUdOdmJXUnZjbVJsYm1SaGJuUmxiblJsY21SbGJuUmxiblJsY21SbGJuUmxibVJsIn0=" # Mock Base64 JWT
} | ConvertTo-Json

Write-Host "[!] Initiating Project Ghost-Walk Simulation..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/capture" -Method Post -Body $simData -ContentType "application/json"
    Write-Host "[+] Simulation Data Ingested. Redirecting to: $($response.redirect)" -ForegroundColor Green
}
catch {
    Write-Error "[-] Simulation Failed: $($_.Exception.Message)"
}
