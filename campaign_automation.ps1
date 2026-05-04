# campaign_automation.ps1
# Run all campaign steps: generate lures, send lures, collect/report clicks, email results

# 1. Generate new lure variants
python generate_lure_variants.py

# 2. (Optional) Send lures (simulate or real)
pwsh -File send_lures.ps1

# 3. Collect and report click results
python phish_report_export.py

# 4. Email campaign results to admins
python send_phish_reports.py

Write-Host "[Automation] Campaign workflow complete." -ForegroundColor Green
