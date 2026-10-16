# Explicit opt-in, LIMITED privileges, current user. May prompt as OS policy requires.
$ErrorActionPreference='Stop'
$Launcher=(Resolve-Path (Join-Path $PSScriptRoot 'Start-Ripple-Windows.cmd')).Path
$Command='"'+$Launcher+'"'
& schtasks.exe /Create /F /SC ONLOGON /TN RippleLaptopAlpha /TR $Command /RL LIMITED
if ($LASTEXITCODE -ne 0) { throw 'Task registration failed; see Task Scheduler policy.' }
Write-Host 'Registered RippleLaptopAlpha for logon of current user. To remove: schtasks /Delete /TN RippleLaptopAlpha /F'
