# User-facing Windows x64 runtime bootstrap. No prior Python or Node required.
# Requires internet access to the official Python and Node release servers.
# Intended for operator consent and a trusted copy of the Ripple source.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Set-Location $root
if(-not [Environment]::Is64BitOperatingSystem){throw 'Windows x64 operating system required'}
$runtime=Join-Path $root 'runtime'
New-Item -ItemType Directory -Force $runtime | Out-Null
$pyZip=Join-Path $runtime 'python-3.11.9-embed-amd64.zip'
$pyExe=Join-Path $runtime 'pythonw.exe'
if(-not (Test-Path $pyExe)) {
    Write-Host 'Downloading official CPython 3.11.9 embedded Windows runtime...'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile $pyZip
    Expand-Archive -LiteralPath $pyZip -DestinationPath $runtime -Force
}
$pth=Join-Path $runtime 'python311._pth'
if(-not (Test-Path $pth)){throw 'Python embeddable runtime did not contain python311._pth'}
$lines=Get-Content -LiteralPath $pth
if($lines -notcontains '..'){Add-Content -LiteralPath $pth -Value '..'}
$nodeExe=Join-Path $runtime 'node.exe'
if(-not (Test-Path $nodeExe)) {
    Write-Host 'Downloading official Node 22.16.0 for preserved Ripple neuron execution...'
    $base='https://nodejs.org/dist/v22.16.0'
    $shaFile=Join-Path $runtime 'node-SHASUMS256.txt'
    Invoke-WebRequest -UseBasicParsing -Uri "$base/SHASUMS256.txt" -OutFile $shaFile
    Invoke-WebRequest -UseBasicParsing -Uri "$base/win-x64/node.exe" -OutFile $nodeExe
}
$shaFile=Join-Path $runtime 'node-SHASUMS256.txt'
if (-not (Test-Path $shaFile)) {Invoke-WebRequest -UseBasicParsing -Uri 'https://nodejs.org/dist/v22.16.0/SHASUMS256.txt' -OutFile $shaFile}
$nodeLine=Get-Content $shaFile | Where-Object { $_ -match '  win-x64/node.exe$' } | Select-Object -First 1
if(-not $nodeLine){throw 'Node publisher checksum missing'}
$expected=($nodeLine -split '\s+')[0].ToLowerInvariant()
$actual=(Get-FileHash $nodeExe -Algorithm SHA256).Hash.ToLowerInvariant()
if($expected -ne $actual){throw 'Node executable hash does not match publisher checksum'}
$startScript=Join-Path $root 'Launch-Ripple-Miner.vbs'
$startSource=@'
Set s = WScript.CreateObject("WScript.Shell")
Set f = CreateObject("Scripting.FileSystemObject")
p = f.GetParentFolderName(WScript.ScriptFullName)
exe = p & "\runtime\pythonw.exe"
s.Run Chr(34) & exe & Chr(34) & " " & Chr(34) & p & "\portable_start.py" & Chr(34), 0, False
WScript.Sleep 2000
token = s.ExpandEnvironmentStrings("%USERPROFILE%") & "\.ripple_antminer_v02\api_token.txt"
If f.FileExists(token) Then s.Run "notepad.exe " & Chr(34) & token & Chr(34), 1, False
s.Run "cmd.exe /c start http://127.0.0.1:8877", 0, False
'@
[System.IO.File]::WriteAllText($startScript,$startSource,[System.Text.Encoding]::ASCII)
$stopScript=Join-Path $root 'Stop-Ripple-Miner.cmd'
$stopSource='@echo off' + "`r`n" + '"%~dp0runtime\python.exe" "%~dp0portable_stop.py"' + "`r`n" + 'pause' + "`r`n"
[System.IO.File]::WriteAllText($stopScript,$stopSource,[System.Text.Encoding]::ASCII)
$desktop=[Environment]::GetFolderPath('Desktop')
$shortcut=Join-Path $desktop 'Ripple Personal Miner.lnk'
$wsh=New-Object -ComObject WScript.Shell
$link=$wsh.CreateShortcut($shortcut)
$link.TargetPath="$env:SystemRoot\System32\wscript.exe"
$link.Arguments='"'+$startScript+'"'
$link.WorkingDirectory=$root
$link.Description='Start your personal Ripple Bitcoin mining controller'
$link.Save()
Write-Host 'Runtime installed. Starting Ripple desktop controller...'
& "$env:SystemRoot\System32\wscript.exe" $startScript