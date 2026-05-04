$date = Get-Date -Format 'yyyy-MM-dd_HHmmss'
$archiveDir = ".\logs\archive\GhostWalk_$date"
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
$files = @(
    "ghostwalk_final_remediation_report.md",
    "ghostwalk_final_triage.md",
    "OmniSOC_ITDR_Report_Auto.md",
    "OmniSOC_ITDR_Report_Template.md",
    "globe_threat_arc.json",
    "sovereign_events.json",
    "session_replay_drift.json",
    "captured_tokens.json",
    "credential_dump_event.json",
    "simulate_bec_rules.py",
    "simulate_credential_dump.py",
    "recon_ghostwalk.py",
    "ghostwalk_phase1_status.md"
)
foreach ($file in $files) {
    if (Test-Path $file) { Copy-Item $file $archiveDir -Force }
}
Write-Host "Artifacts archived to $archiveDir"