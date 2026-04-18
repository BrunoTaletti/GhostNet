; Script gerado para o GhostNet
; Requer Inno Setup 6.0 ou superior

#define MyAppName "GhostNet"
#define MyAppPublisher "GhostCore"
#define MyAppExeName "main.exe"

[Setup]
; ATENÇÃO: É vital gerar um AppId único para o seu app!
; No Inno Setup, vá em Tools -> Generate GUID e cole no lugar desse ID abaixo.
AppId={{SUA-GUID-AQUI-GERADA-PELO-INNO-SETUP}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Instala na pasta "Arquivos de Programas" padrão do Windows
DefaultDirName={autopf}\{#MyAppPublisher}\{#MyAppName}
DisableProgramGroupPage=yes
; Pede permissão de administrador para instalar bonitinho no sistema
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=GhostNet_Installer_v{#MyAppVersion}
; Ícone do próprio instalador (usa o mesmo do app)
SetupIconFile=app-icon.ico
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Puxa o executável principal
Source: "dist\main\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Puxa TODO o resto da pasta (DLLs, imagens, txt de versão)
Source: "dist\main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Cria o atalho no Menu Iniciar
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app-icon.ico"
; Cria o atalho na Área de Trabalho
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\app-icon.ico"

[Run]
; Oferece a opção de abrir o app assim que a instalação terminar
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent