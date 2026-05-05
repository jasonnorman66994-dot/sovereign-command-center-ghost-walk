$ErrorActionPreference = 'Stop'

$runnerRoot = 'C:\actions-runner'
$runnerScript = Join-Path $runnerRoot 'run.cmd'
$taskName = 'GitHubRunner_Sovereign'

if (-not (Test-Path $runnerScript)) {
    throw "Runner script not found at $runnerScript"
}

$action = New-ScheduledTaskAction -Execute $runnerScript -WorkingDirectory $runnerRoot
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings | Out-Null

Start-ScheduledTask -TaskName $taskName
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State, Author