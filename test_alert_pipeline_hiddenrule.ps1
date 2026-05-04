# test_alert_pipeline_hiddenrule.ps1
# PowerShell script to test the alert pipeline with a HiddenInboxRule alert

$testPayload = @{
    username      = "carol@example.com"
    password      = "NotApplicable"
    landingUrl    = "https://outlook.office.com/mail/inbox"
    userAgent     = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
    remoteAddress = "198.51.100.77"
    customType    = "HiddenInboxRule"
    campaign      = "InboxRuleTest2026"
    extraContext  = "Rule: AutoForwardAll, ForwardTo: attacker@evil.com"
    alertType     = "HiddenInboxRule"
    severity      = "High"
    details       = "A hidden inbox rule was created to auto-forward all mail."
} | ConvertTo-Json

Write-Host "[!] Sending HiddenInboxRule test alert payload to pipeline..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/capture" -Method Post -Body $testPayload -ContentType "application/json"
    Write-Host "[+] Test alert submitted. Redirect: $($response.redirect)" -ForegroundColor Green
}
catch {
    Write-Error "[-] Test submission failed: $($_.Exception.Message)"
}
