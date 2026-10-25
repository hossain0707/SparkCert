; SparkCert development-preview installer. The executable is NOT code signed.
#define AppName "SparkCert"
#define AppVersion "0.2.1"
#define AppPublisher "Md Najmul Hossain"
#define AppURL "https://github.com/hossain0707/SparkCert"

[Setup]
AppId={{E22B38BD-3F19-48DE-AD97-C6A2FD897BD3}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion} Preview (Unsigned)
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={localappdata}\Programs\SparkCert
DefaultGroupName=SparkCert
OutputDir=..\dist\release
OutputBaseFilename=SparkCert-Setup-Windows-x64
SetupIconFile=..\assets\sparkcert-icon.ico
UninstallDisplayIcon={app}\SparkCert.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
DisableProgramGroupPage=yes
DisableWelcomePage=no
CloseApplications=yes
; No shell execution or machine-wide registry modification during install.

[Files]
Source: "..\dist\SparkCert\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\SparkCert"; Filename: "{app}\SparkCert.exe"
Name: "{autodesktop}\SparkCert"; Filename: "{app}\SparkCert.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\SparkCert.exe"; Description: "Launch SparkCert"; Flags: nowait postinstall skipifsilent
