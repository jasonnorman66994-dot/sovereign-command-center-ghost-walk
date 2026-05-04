# test_alert_pipeline.ps1
# PowerShell script to test the full alert pipeline with a sample payload

$testPayload = @{
    username      = "testuser@contoso.com"
    password      = "TestPassword!2026"
    landingUrl    = "https://login.phish-portal.com/abc123"
    userAgent     = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    remoteAddress = "203.0.113.55"
    customType    = "Credential_Harvest"
    campaign      = "TestCampaign2026"
    extraContext  = "dGVzdF90b2tlbl9kYXRhX2Zvcl9wYXlsaW5lIg==" # base64 mock token
} | ConvertTo-Json

Write-Host "[!] Sending test alert payload to pipeline..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/capture" -Method Post -Body $testPayload -ContentType "application/json"
    Write-Host "[+] Test alert submitted. Redirect: $($response.redirect)" -ForegroundColor Green
}
catch {
    Write-Error "[-] Test submission failed: $($_.Exception.Message)"
}
