; ============================================================
;  Ajouby PDF - shared app-language page for the installers
;  Included by installer_win10.iss and installer_win7.iss
;
;  Setup asks for its own UI language first (Arabic/English)
;  and this page then asks which language the application
;  should use. The choice is written to {app}\language.txt
;  and read by the app on its next start.
;
;  Silent installs can pass /APPLANG=ar (or en, fr, ...).
; ============================================================

[Code]
var
  LangPage: TWizardPage;
  LangCombo: TNewComboBox;
  LangHint: TNewStaticText;
  LangCodes: array[0..31] of String;
  LangNames: array[0..31] of String;
  LangCount: Integer;

function GetUserDefaultUILanguage: Word;
  external 'GetUserDefaultUILanguage@kernel32.dll stdcall';

function DetectLanguage: String;
var
  LangID: Word;
begin
  LangID := GetUserDefaultUILanguage and $3FF;
  case LangID of
    1:  Result := 'ar';  { Arabic }
    4:  Result := 'zh';  { Chinese }
    7:  Result := 'de';  { German }
    8:  Result := 'el';  { Greek }
    9:  Result := 'en';  { English }
    10: Result := 'es';  { Spanish }
    12: Result := 'fr';  { French }
    16: Result := 'it';  { Italian }
    17: Result := 'ja';  { Japanese }
    18: Result := 'ko';  { Korean }
    19: Result := 'nl';  { Dutch }
    21: Result := 'pl';  { Polish }
    22: Result := 'pt';  { Portuguese }
    25: Result := 'ru';  { Russian }
    29: Result := 'sv';  { Swedish }
    31: Result := 'tr';  { Turkish }
    34: Result := 'uk';  { Ukrainian }
    41: Result := 'fa';  { Persian }
    57: Result := 'hi';  { Hindi }
  else
    Result := '';
  end;
end;

procedure AddLanguage(const Code, Name: String);
begin
  if LangCount <= High(LangCodes) then
  begin
    LangCodes[LangCount] := Code;
    LangNames[LangCount] := Name;
    LangCount := LangCount + 1;
  end;
end;

function FindLanguage(const Code: String): Integer;
var
  I: Integer;
begin
  Result := -1;
  for I := 0 to LangCount - 1 do
    if Lowercase(LangCodes[I]) = Lowercase(Code) then
    begin
      Result := I;
      Exit;
    end;
end;

function SetupLanguageCode: String;
var
  Name: String;
begin
  Name := Lowercase(ExpandConstant('{language}'));
  if Name = 'arabic' then
    Result := 'ar'
  else if Name = 'english' then
    Result := 'en'
  else
    Result := '';
end;

function ChosenLanguage: String;
var
  LangOverride: String;
  Index: Integer;
begin
  LangOverride := Lowercase(ExpandConstant('{param:APPLANG|}'));
  if LangOverride <> '' then
  begin
    Index := FindLanguage(LangOverride);
    if Index >= 0 then
    begin
      Result := LangCodes[Index];
      Exit;
    end;
  end;

  if (LangCombo <> nil) and (LangCombo.ItemIndex >= 0) then
  begin
    Result := LangCodes[LangCombo.ItemIndex];
    Exit;
  end;

  Result := SetupLanguageCode;
  if Result = '' then
    Result := DetectLanguage;
  if Result = '' then
    Result := 'en';
end;

procedure InitializeWizard;
var
  I, Index: Integer;
  Preferred: String;
begin
  LangCount := 0;
  AddLanguage('ar', 'العربية (Arabic)');
  AddLanguage('en', 'English');
  AddLanguage('fr', 'Français (French)');
  AddLanguage('es', 'Español (Spanish)');
  AddLanguage('de', 'Deutsch (German)');
  AddLanguage('it', 'Italiano (Italian)');
  AddLanguage('pt', 'Português (Portuguese)');
  AddLanguage('tr', 'Türkçe (Turkish)');
  AddLanguage('ru', 'Русский (Russian)');
  AddLanguage('zh', '中文（简体）(Chinese)');
  AddLanguage('ja', '日本語 (Japanese)');
  AddLanguage('ko', '한국어 (Korean)');
  AddLanguage('hi', 'हिन्दी (Hindi)');
  AddLanguage('nl', 'Nederlands (Dutch)');
  AddLanguage('pl', 'Polski (Polish)');
  AddLanguage('sv', 'Svenska (Swedish)');
  AddLanguage('el', 'Ελληνικά (Greek)');
  AddLanguage('fa', 'فارسی (Persian)');
  AddLanguage('uk', 'Українська (Ukrainian)');

  LangPage := CreateCustomPage(wpWelcome,
    'لغة البرنامج — Application language',
    'اختر اللغة التي ستُفتح بها واجهة Ajouby PDF. يمكنك تغييرها لاحقاً.' + #13#10 +
    'Choose the language Ajouby PDF will use. You can change it later.');

  LangCombo := TNewComboBox.Create(LangPage);
  LangCombo.Parent := LangPage.Surface;
  LangCombo.Left := 0;
  LangCombo.Top := ScaleY(8);
  LangCombo.Width := LangPage.SurfaceWidth;
  LangCombo.Style := csDropDownList;
  for I := 0 to LangCount - 1 do
    LangCombo.Items.Add(LangNames[I]);

  { /APPLANG=... wins, then the setup UI language, then Windows }
  Preferred := Lowercase(ExpandConstant('{param:APPLANG|}'));
  if Preferred = '' then
    Preferred := SetupLanguageCode;
  if Preferred = '' then
    Preferred := DetectLanguage;
  Index := FindLanguage(Preferred);
  if Index < 0 then
    Index := FindLanguage('en');
  LangCombo.ItemIndex := Index;

  LangHint := TNewStaticText.Create(LangPage);
  LangHint.Parent := LangPage.Surface;
  LangHint.Left := 0;
  LangHint.Top := LangCombo.Top + LangCombo.Height + ScaleY(10);
  LangHint.AutoSize := False;
  LangHint.WordWrap := True;
  LangHint.Width := LangPage.SurfaceWidth;
  LangHint.Caption :=
    'يمكنك تغيير اللغة في أي وقت من قائمة «اللغة» داخل البرنامج.' + #13#10 +
    'You can change the language at any time from the Language menu inside the app.';
  LangHint.AdjustHeight;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Code: String;
begin
  if CurStep = ssPostInstall then
  begin
    Code := ChosenLanguage;
    if FindLanguage(Code) < 0 then
      Code := 'en';
    SaveStringToFile(ExpandConstant('{app}\language.txt'), Code, False);
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\language.txt"
