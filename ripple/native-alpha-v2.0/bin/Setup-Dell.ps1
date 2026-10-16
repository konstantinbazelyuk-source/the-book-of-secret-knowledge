# Run by user, no administrator rights required. No background service is silently installed.
$ErrorActionPreference='Stop'
$Base=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $Base
Write-Host 'Ripple Laptop Native Alpha - local setup (Windows)'
if (!(Get-Command py -ErrorAction SilentlyContinue) -and !(Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python 3.11+ not available. Install Python from python.org, then rerun.' }
$Python = 'python'
if (Get-Command py -ErrorAction SilentlyContinue) { $Python='py' }
if ($Python -eq 'py') { & py -3 -m venv .venv } else { & python -m venv .venv }
$VenvPython=Join-Path $Base '.venv\Scripts\python.exe'
if (!(Test-Path $VenvPython)) { throw 'Virtual environment creation failed' }
& $VenvPython -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
if ($LASTEXITCODE -ne 0) { throw 'Python must be 3.11 or newer' }
& $VenvPython -m pip install -r (Join-Path $Base 'requirements.txt')
if ($LASTEXITCODE -ne 0) { Write-Warning 'psutil could not be installed. A reduced hardware probe can still run.' }
if (!(Get-Command node -ErrorAction SilentlyContinue)) { Write-Warning 'Node.js 20+ is required for the preserved Ripple modules. Install from nodejs.org.' } else { $MajorNode=[int]((& node --version).TrimStart('v').Split('.')[0]); if ($MajorNode -lt 20) { Write-Warning 'Detected Node.js is older than 20; update to use locked Ripple code.' } }
& $VenvPython -m ripple_native probe | Out-File -Encoding UTF8 (Join-Path $Base 'dell_probe_local.json')
Write-Host 'Created dell_probe_local.json from THIS machine. Inspect before activating sustained workloads.'
& $VenvPython -m unittest discover -s tests -p 'test_*.py' -v
Write-Host 'To start: .\bin\Start-Ripple-Windows.cmd'
Write-Host 'For optional login startup: .\bin\Register-AtLogon.ps1 (user action required).'
