[Setup]
AppName=Pente
AppVerName=0.1
DefaultDirName={pf}\Gamatronix\Pente
DefaultGroupName=Gamatronix
ShowLanguageDialog=yes
SetupIconFile=D:\gamoto\python\pente\dist\gamatronix.ico
OutputDir=D:\gamoto\python\pente\deploy
VersionInfoVersion=0.1
VersionInfoCompany=Gamatronix
VersionInfoDescription=Pente board game by Gamatronix
VersionInfoTextVersion=Beta version 0.1
[Files]
Source: dist\*.*; DestDir: {app}
[Tasks]
Name: desktopicon; Description: Create a &desktop Icon; GroupDescription: Additional icons:; Flags: unchecked
[Icons]
Name: {userdesktop}\Pente; Filename: {app}\pente.exe; WorkingDir: {app}; IconFilename: {app}\gamatronix.ico; Tasks: desktopicon
Name: {group}\Pente; Filename: {app}\pente.exe; WorkingDir: {app}; IconFilename: {app}\gamatronix.ico; Tasks: 
[Run]
Filename: {app}\pente.exe; WorkingDir: {app}; StatusMsg: Launching Pente...; Flags: nowait postinstall skipifsilent; Tasks: 
