# Entry point from repository's ripple directory. Works without administrator rights.
$ErrorActionPreference = 'Stop'
$Root = Join-Path $PSScriptRoot 'native-alpha-v2.0'
if (!(Test-Path (Join-Path $Root 'bin/Setup-Dell.ps1'))) { throw 'Native Ripple runtime missing' }
Push-Location $Root
try { & (Join-Path $Root 'bin/Setup-Dell.ps1') } finally { Pop-Location }
Write-Host 'Setup finished. See native-alpha-v2.0/README.md before starting the runtime.'
