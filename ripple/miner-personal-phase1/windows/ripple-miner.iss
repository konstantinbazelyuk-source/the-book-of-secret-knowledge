#define MyAppName "Ripple Personal Miner"
#define MyAppVersion "1.0.0-beta"
#define MyAppPublisher "FireClay Studio"
#define MyAppExeName "RippleDesktop.exe"
[Setup]
AppId={{F7245D82-BDA0-4EB5-ADBF-FCD999E02429}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Ripple Personal Miner
DefaultGroupName={#MyAppName}
OutputDir=..\dist\installer
OutputBaseFilename=RipplePersonalMinerSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
UninstallDisplayIcon={app}\RippleDesktop\RippleDesktop.exe
[Files]
Source: "..\dist\RippleDesktop\*"; DestDir: "{app}\RippleDesktop"; Flags: recursesubdirs createallsubdirs
Source: "..\dist\RippleWorker\*"; DestDir: "{app}\RippleWorker"; Flags: recursesubdirs createallsubdirs
Source: "..\dist\node\node.exe"; DestDir: "{app}\node"; Flags: ignoreversion
[Icons]
Name: "{group}\Ripple Personal Miner"; Filename: "{app}\RippleDesktop\RippleDesktop.exe"
Name: "{autodesktop}\Ripple Personal Miner"; Filename: "{app}\RippleDesktop\RippleDesktop.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: checkedonce
[Run]
Filename: "{app}\RippleDesktop\RippleDesktop.exe"; Description: "Start Ripple Personal Miner"; Flags: nowait postinstall skipifsilent
[UninstallDelete]
; Deliberately leave %USERPROFILE%\.ripple_antminer_v02 and saved history untouched.