# Windows x64 build host required. Builds two genuine frozen executables and
# an Inno Setup installer. Does not perform cryptocurrency mining in CI.
param([string]$Python='py',[string]$InnoCompiler='')
$ErrorActionPreference='Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
& $Python -3.11 -m pip install --upgrade 'pyinstaller>=6.10,<7' 'psutil>=6,<8'
if($LASTEXITCODE -ne 0){throw 'Python build dependencies failed'}
$extra=@('--add-data','legacy;legacy','--add-data','ripple_miner/neuron_bridge.cjs;ripple_miner')
& $Python -3.11 -m PyInstaller --noconfirm --clean --onedir --windowed --name RippleDesktop `
     --add-data 'web;web' @extra ripple_desktop.py
if($LASTEXITCODE -ne 0){throw 'Desktop executable build failed'}
$native=@()
if(Test-Path 'native/ripple_sha256d.dll'){$native=@('--add-binary','native/ripple_sha256d.dll;native')}
& $Python -3.11 -m PyInstaller --noconfirm --clean --onedir --console --name RippleWorker `
     @extra @native ripple_worker.py
if($LASTEXITCODE -ne 0){throw 'Worker executable build failed'}
# Explicit Node binary with TLS download and the publisher's checksum listing.
# Match checksum filename exactly. Both requests use HTTPS.
$nodever='v22.16.0'
$base="https://nodejs.org/dist/$nodever"
$checksumUrl="$base/SHASUMS256.txt"
$nodeUrl="$base/win-x64/node.exe"
New-Item -ItemType Directory -Force 'dist/node' | Out-Null
Invoke-WebRequest -Uri $checksumUrl -OutFile 'dist/node/SHASUMS256.txt'
Invoke-WebRequest -Uri $nodeUrl -OutFile 'dist/node/node.exe'
$line=Get-Content 'dist/node/SHASUMS256.txt' | Where-Object { $_ -match '  win-x64/node.exe$' } | Select-Object -First 1
if(!$line){throw 'Node publisher checksum not found'}
$expected=($line -split '\s+')[0].ToLowerInvariant()
$actual=(Get-FileHash 'dist/node/node.exe' -Algorithm SHA256).Hash.ToLowerInvariant()
if($expected -ne $actual){throw 'Node binary checksum mismatch'}
$inno=$InnoCompiler
if(!$inno){$inno="${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"}
if(!(Test-Path $inno)){
  Write-Host 'Portable folder ready under dist/. Install Inno Setup 6 on the Windows build host for Setup.exe.'
  exit 0
}
& $inno 'windows/ripple-miner.iss'
if($LASTEXITCODE -ne 0){throw 'Inno Setup compilation failed'}
Write-Host 'Windows installer created in dist/installer. Run clean-machine validation before publishing.'