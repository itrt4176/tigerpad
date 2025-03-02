; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "TigerPad Relay"
#ifndef MyAppVersion
  #define MyAppVersion "dev"
#endif
#define MyAppPublisher "Iron Tigers Robotics Team"
#define MyAppURL "https://github.com/itrt4176/tigerpad"
#define PyVersion "3.12.9"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{0D751830-454B-4551-B00B-1A03C390CD3C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
ArchitecturesAllowed=x64compatible
DefaultDirName={sd}\Users\Public\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
MinVersion=10.0
; Uncomment the following line to run in non administrative install mode (install for current user only).
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputBaseFilename=relay-setup_{#MyAppVersion}_x64
OutputDir=dist
SetupIconFile=relay\res\tigerpad.ico
SolidCompression=yes
SourceDir=..\
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "*"; Excludes: "\build,\dist,__pycache__,.*,*.iss,"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autodesktop}\TigerPad Relay"; Filename: "{app}\scripts\run_relay.vbs"; WorkingDir: "{app}"; IconFilename: "{app}\relay\res\tigerpad.ico"
Name: "{group}\TigerPad Relay"; Filename: "{app}\scripts\run_relay.vbs"; WorkingDir: "{app}"; IconFilename: "{app}\relay\res\tigerpad.ico"
Name: "{autostartup}\TigerPad Relay"; Filename: "{app}\scripts\run_relay.vbs"; WorkingDir: "{app}"; IconFilename: "{app}\relay\res\tigerpad.ico"

[Run]
Filename: "{tmp}\vs_buildtools.exe"; Parameters: "--norestart --quiet --wait --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.MSBuildTools"; StatusMsg: "Installing VS Build Tools..."; Check: FileExists(ExpandConstant('{tmp}\vs_buildtools.exe'));
Filename: "{tmp}\python-{#PyVersion}-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1"; StatusMsg: "Installing Python {#PyVersion}..."; Check: FileExists(ExpandConstant('{tmp}\python-{#PyVersion}-amd64.exe'));
Filename: "{app}\scripts\setup_venv.bat"; WorkingDir: "{app}"; Flags: runasoriginaluser shellexec runhidden waituntilterminated
Filename: "{app}\scripts\run_relay.bat"; WorkingDir: "{app}"; Description: "Start TigerPad Relay"; Flags: postinstall runhidden shellexec

[Code]
var
  DownloadPage: TDownloadWizardPage;

function OnDownloadProgress(const Url, FileName: String; const Progress, ProgressMax: Int64): Boolean;
begin
  if Progress = ProgressMax then
    Log(Format('Successfully downloaded file to {tmp}: %s', [FileName]));
  Result := True;
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), @OnDownloadProgress);
  DownloadPage.ShowBaseNameInsteadOfUrl := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
    DownloadCount: Integer;

begin
  if CurPageID = wpReady then begin
    DownloadCount := 0;
    DownloadPage.Clear;
    
    if FileSearch('cl.exe', GetEnv('PATH')) = '' then begin
        DownloadPage.Add('https://aka.ms/vs/17/release/vs_BuildTools.exe', 'vs_buildtools.exe', '');
        DownloadCount := DownloadCount + 1;
    end;
    
    if FileSearch('python.exe', GetEnv('PATH')) = '' then begin
        DownloadPage.Add('https://www.python.org/ftp/python/{#PyVersion}/python-{#PyVersion}-amd64.exe', 'python-{#PyVersion}-amd64.exe', '');
        DownloadCount := DownloadCount + 1;
    end;
    
    if DownloadCount >= 1 then begin
        DownloadPage.Show;
        try
          try
            DownloadPage.Download; // This downloads the files to {tmp}
            Result := True;
          except
            if DownloadPage.AbortedByUser then
              Log('Aborted by user.')
            else
              SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
            Result := False;
          end;
        finally
          DownloadPage.Hide;
        end;
    end else
        Result := True;
  end else
    Result := True;
end;
