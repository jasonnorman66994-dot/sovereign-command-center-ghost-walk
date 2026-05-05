$ErrorActionPreference = 'Stop'

$runnerRoot = 'C:\actions-runner'
$runnerScript = Join-Path $runnerRoot 'run.cmd'
$taskWrapper = Join-Path $runnerRoot 'start-runner.cmd'
$taskName = 'GitHubRunner_Sovereign'
$cmdExe = Join-Path $env:SystemRoot 'System32\cmd.exe'
$systemPath = @(
    (Join-Path $env:SystemRoot 'System32'),
    (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0'),
    $runnerRoot,
    '%PATH%'
) -join ';'

if (-not (Test-Path $runnerScript)) {
    throw "Runner script not found at $runnerScript"
}

if (-not (Test-Path $cmdExe)) {
    throw "cmd.exe not found at $cmdExe"
}

$wrapperContent = @(
    '@echo off',
    'setlocal',
    ('set "PATH=' + $systemPath + '"'),
    'call "C:\actions-runner\run.cmd"',
    'exit /b %ERRORLEVEL%'
) -join "`r`n"

Set-Content -Path $taskWrapper -Value $wrapperContent -Encoding ASCII

$action = New-ScheduledTaskAction -Execute $cmdExe -Argument "/c `"$taskWrapper`"" -WorkingDirectory $runnerRoot
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