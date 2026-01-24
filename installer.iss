; Script de Inno Setup para Fichaje Zaragonjg
; Instalador profesional para Windows

#define MyAppName "Fichaje Zaragonjg"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Zaragonjg"
#define MyAppURL "https://github.com/Willer1285/Fichaje"
#define MyAppExeName "FichajeZaragonjg.exe"

[Setup]
; Información de la aplicación
AppId={{8F2A3B4C-5D6E-7F8A-9B0C-1D2E3F4A5B6C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=FichajeZaragonjg_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

; Configuración de desinstalación
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Crear icono en inicio rápido"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ejecutable principal (generado con PyInstaller)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Archivos adicionales si existen (dependencias externas)
; Source: "dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icono
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Documentación (opcional)
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Verificar si la aplicación está en ejecución antes de instalar/desinstalar
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  // Verificar si el proceso está en ejecución
  if CheckForMutexes('Global\FichajeZaragonjg') then
  begin
    MsgBox('Fichaje Zaragonjg está actualmente en ejecución. Por favor cierre la aplicación antes de continuar.', mbError, MB_OK);
    Result := False;
  end;
end;

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if CheckForMutexes('Global\FichajeZaragonjg') then
  begin
    MsgBox('Fichaje Zaragonjg está actualmente en ejecución. Por favor cierre la aplicación antes de desinstalar.', mbError, MB_OK);
    Result := False;
  end;
end;
