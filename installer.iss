[Setup]
AppName=VCM Zeitmessung
AppVersion=1.0.0
DefaultDirName={pf}\VCM Zeitmessung
DefaultGroupName=VCM Zeitmessung
UninstallDisplayIcon={app}\VCM-Zeitmessung.exe
PrivilegesRequired=admin
OutputDir=installer
OutputBaseFilename=VCM-Zeitmessung-Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\VCM-Zeitmessung\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\VCM Zeitmessung"; Filename: "{app}\VCM-Zeitmessung.exe"
Name: "{commondesktop}\VCM Zeitmessung"; Filename: "{app}\VCM-Zeitmessung.exe"

[Run]
Filename: "{app}\VCM-Zeitmessung.exe"; Description: "VCM Zeitmessung starten"; Flags: nowait postinstall skipifsilent
