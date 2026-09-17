#define MyAppName "Gujarati Legacy Font Converter"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Passion Projects"
#define MyAppExeName "GujaratiLegacyFontConverter.exe"

[Setup]
AppId={{9C2D2B6B-8C5B-4D4A-9D6A-1310131A4B7C}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/VishalGujarati
DefaultDirName={pf}\Gujarati Legacy Font Converter
DefaultGroupName={#MyAppName}
OutputBaseFilename=GujaratiLegacyFontConverter-1.0.1-Setup-x64
OutputDir=..\Output
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\assets\software_logo.ico
LicenseFile=..\LICENSE.txt
PrivilegesRequired=admin

[Files]
Source: "..\dist\GujaratiLegacyFontConverter\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD-PARTY-NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
