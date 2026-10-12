@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ENGINE=C:\Program Files\Epic Games\UE_5.7\Engine"
set "UECMD=%ENGINE%\Binaries\Win64\UnrealEditor-Cmd.exe"
set "UBT=%ENGINE%\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
set "UAT=%ENGINE%\Build\BatchFiles\RunUAT.bat"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "REPO=%~dp0..\.."
set "DISCOVERY=%~dp0..\unreal\p0_boss_04_discover_integration.py"
set "DECIDE=%~dp0..\ci\p0_boss_04_decide_promotion.py"
set "PATCH=%~dp0..\ci\p0_boss_04_patch_native_source.py"
set "ARCHIVE=%PROJECT%\Builds\NARIS_Win64_Dev"
set "PACKAGED=%ARCHIVE%\Windows\NARIS.exe"
set "BOSS_QA_LOG=%PROJECT%\Reports\P0-BOSS-04_boss_qa.log"
set "PACKAGED_QA_LOG=%PROJECT%\Reports\P0-BOSS-04_packaged_combat_qa.log"
set "FINAL=%PROJECT%\Reports\P0-BOSS-04_final_acceptance.json"

echo ============================================================
echo CALL OF NARIS - P0-BOSS-04 ASH WARDEN NATIVE PROMOTION
echo Visual Approval -> Discovery -> Fingerprint Patch -> Regression
echo ============================================================

for %%F in ("%UECMD%" "%UBT%" "%UAT%" "%UPROJECT%" "%DISCOVERY%" "%DECIDE%" "%PATCH%") do (
  if not exist "%%~F" (
    echo [ASH-WARDEN-04] FAIL missing: %%~F
    exit /b 150
  )
)

echo [1/7] Refreshing read-only integration discovery...
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%DISCOVERY%" -stdout -FullStdOutLogOutput
if errorlevel 1 exit /b 151

echo [2/7] Evaluating visual/evidence/integration decision...
python "%DECIDE%" --project-root "%PROJECT%" --repo-root "%REPO%"
if errorlevel 1 (
  echo [ASH-WARDEN-04] BLOCKED: decision gate did not authorize promotion.
  exit /b 152
)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%PROJECT%\Reports\P0-BOSS-04_decision.json'|ConvertFrom-Json;" ^
 "if($j.status -ne 'READY' -or $j.decision -ne 'READY_NATIVE_CXX_PATCH' -or $j.replacement_allowed -ne $true){exit 153};" ^
 "Write-Host ('[ASH-WARDEN-04] Decision='+$j.decision);" ^
 "Write-Host ('[ASH-WARDEN-04] Source SHA='+$j.source_evidence.cpp_sha256)"
if errorlevel 1 exit /b 153

echo [3/7] Applying constructor-only fingerprinted source patch...
python "%PATCH%" --project-root "%PROJECT%" --mode apply
if errorlevel 1 exit /b 154
set "PATCH_APPLIED=1"

set "ComSpec=C:\Windows\System32\cmd.exe"
set "SHELL=%ComSpec%"

echo [4/7] Building NARIS Win64 Development...
"%UBT%" NARIS Win64 Development -Project="%UPROJECT%" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 (
  set "FAIL_REASON=win64_build_failed"
  goto :rollback
)

echo [5/7] Running editor boss Phase 2 QA...
if exist "%BOSS_QA_LOG%" del /q "%BOSS_QA_LOG%"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$p=Start-Process -FilePath '%UECMD%' -ArgumentList @('%UPROJECT%','/Game/NARIS/Maps/L_AshMap_Assembly','-game','-nullrhi','-unattended','-nop4','-nosplash','-NARISBOSSQA','-abslog=%BOSS_QA_LOG%') -PassThru;" ^
 "if(-not $p.WaitForExit(25000)){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue};" ^
 "Start-Sleep -Seconds 1"
if not exist "%BOSS_QA_LOG%" (
  set "FAIL_REASON=boss_qa_log_missing"
  goto :rollback
)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$l='%BOSS_QA_LOG%';$t=Get-Content -Raw -LiteralPath $l;" ^
 "if($t -notmatch 'NARIS_BOSS_ART_READY Mesh=SK_NARIS_AshWarden_Production'){exit 161};" ^
 "if($t -notmatch 'NARIS_BOSS_QA Spawned=1'){exit 162};" ^
 "if($t -notmatch 'NARIS_BOSS_PHASE2'){exit 163};" ^
 "if($t -match 'Fatal error:|LowLevelFatalError|Unhandled Exception|Assertion failed:'){exit 164};" ^
 "Write-Host '[ASH-WARDEN-04] Native art + Phase2 QA PASS'"
if errorlevel 1 (
  set "FAIL_REASON=boss_phase2_qa_failed"
  goto :rollback
)

echo [6/7] Cleaning Cook / Stage / Archive outputs...
for %%D in ("%PROJECT%\Saved\Cooked\Windows" "%PROJECT%\Saved\StagedBuilds\Windows" "%ARCHIVE%\Windows") do (
  if exist "%%~D" (
    rd /s /q "%%~D"
    if exist "%%~D" (
      set "FAIL_REASON=clean_outputs_failed"
      goto :rollback
    )
  )
)

echo [6/7] Full Cook / Stage / Pak / Archive...
"%UAT%" BuildCookRun -project="%UPROJECT%" -noP4 -platform=Win64 -clientconfig=Development -skipbuild -cook -stage -pak -archive -archivedirectory="%ARCHIVE%" -map=/Game/NARIS/Maps/L_AshMap_Assembly -unattended -utf8output
if errorlevel 1 (
  set "FAIL_REASON=package_failed"
  goto :rollback
)
if not exist "%PACKAGED%" (
  set "FAIL_REASON=packaged_exe_missing"
  goto :rollback
)

echo [7/7] Packaged D3D12 combat + boss-art regression...
if exist "%PACKAGED_QA_LOG%" del /q "%PACKAGED_QA_LOG%"
"%PACKAGED%" -unattended -nosplash -windowed -ResX=1280 -ResY=720 -d3d12 -NARISCOMBATQA -abslog="%PACKAGED_QA_LOG%"
if errorlevel 1 (
  set "FAIL_REASON=packaged_runtime_failed"
  goto :rollback
)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$l='%PACKAGED_QA_LOG%';if(-not(Test-Path -LiteralPath $l)){exit 171};$t=Get-Content -Raw -LiteralPath $l;" ^
 "if($t -notmatch 'NARIS_COMBAT_QA_RESULT Pass=1'){exit 172};" ^
 "if($t -notmatch 'NARIS_BOSS_ART_READY Mesh=SK_NARIS_AshWarden_Production'){exit 173};" ^
 "if($t -match 'Fatal error:|LowLevelFatalError|Unhandled Exception|Assertion failed:'){exit 174};" ^
 "Write-Host '[ASH-WARDEN-04] Packaged D3D12 regression PASS'"
if errorlevel 1 (
  set "FAIL_REASON=packaged_log_qa_failed"
  goto :rollback
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$patch=Get-Content -Raw -LiteralPath '%PROJECT%\Reports\P0-BOSS-04_native_patch.json'|ConvertFrom-Json;" ^
 "$decision=Get-Content -Raw -LiteralPath '%PROJECT%\Reports\P0-BOSS-04_decision.json'|ConvertFrom-Json;" ^
 "$o=[ordered]@{" ^
 " schema_version='1.0.0';status='PASS';promoted=$true;product='CALL OF NARIS';boss='Ash Warden';" ^
 " integration='native_cpp_constructor_patch';source_before_sha256=$patch.before_cpp_sha256;source_after_sha256=$patch.after_cpp_sha256;" ^
 " candidate_mesh=$patch.candidate_mesh;visual_evidence=$decision.screenshot;boss_phase2_qa=$true;packaged_combat_qa=$true;" ^
 " build='NARIS Win64 Development';package='Full Clean Cook/Stage/Pak/Archive';rollback_backup=$patch.backup_path;" ^
 "};$o|ConvertTo-Json -Depth 8|Set-Content -Encoding utf8NoBOM -LiteralPath '%FINAL%'"
echo ============================================================
echo [ASH-WARDEN-04] PASS - UNIQUE ASH WARDEN SURVIVED PACKAGE QA
echo ============================================================
exit /b 0

:rollback
echo [ASH-WARDEN-04] FAILURE: !FAIL_REASON!
echo [ASH-WARDEN-04] Restoring fingerprinted NarisCreature.cpp backup...
python "%PATCH%" --project-root "%PROJECT%" --mode rollback
set "RB=%ERRORLEVEL%"
if not "%RB%"=="0" (
  echo [ASH-WARDEN-04] CRITICAL: source rollback failed.
  exit /b 199
)

echo [ASH-WARDEN-04] Rebuilding restored source...
"%UBT%" NARIS Win64 Development -Project="%UPROJECT%" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 exit /b 198

echo [ASH-WARDEN-04] Restoring clean packaged baseline...
for %%D in ("%PROJECT%\Saved\Cooked\Windows" "%PROJECT%\Saved\StagedBuilds\Windows" "%ARCHIVE%\Windows") do (
  if exist "%%~D" rd /s /q "%%~D"
)
"%UAT%" BuildCookRun -project="%UPROJECT%" -noP4 -platform=Win64 -clientconfig=Development -skipbuild -cook -stage -pak -archive -archivedirectory="%ARCHIVE%" -map=/Game/NARIS/Maps/L_AshMap_Assembly -unattended -utf8output
if errorlevel 1 exit /b 197

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$o=[ordered]@{schema_version='1.0.0';status='FAIL';promoted=$false;failure_reason='!FAIL_REASON!';rollback='PASS';restored_package=$true};" ^
 "$o|ConvertTo-Json|Set-Content -Encoding utf8NoBOM -LiteralPath '%FINAL%'"
echo [ASH-WARDEN-04] Rollback PASS. Existing proxy restored.
exit /b 190
