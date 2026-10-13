@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ENGINE=C:\Program Files\Epic Games\UE_5.7\Engine"
set "UECMD=%ENGINE%\Binaries\Win64\UnrealEditor-Cmd.exe"
set "UBT=%ENGINE%\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
set "UAT=%ENGINE%\Build\BatchFiles\RunUAT.bat"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "PROMOTE=%~dp0..\unreal\p0_05_promote_hero.py"
set "ROLLBACK=%~dp0..\unreal\p0_05_rollback_hero.py"
set "APPROVAL=%~dp0..\..\data\P0_HERO_VISUAL_APPROVAL.json"
set "ARCHIVE=%PROJECT%\Builds\NARIS_Win64_Dev"
set "PACKAGED=%ARCHIVE%\Windows\NARIS.exe"
set "PACKAGED_INTERNAL=%ARCHIVE%\Windows\NARIS\Binaries\Win64\NARIS.exe"
set "QA_LOG=%PROJECT%\Reports\P0-05_packaged_combat_qa.log"
set "PROMOTION_REPORT=%PROJECT%\Reports\P0-05_promotion.json"
set "ROLLBACK_REPORT=%PROJECT%\Reports\P0-05_rollback.json"
set "REPORT=%PROJECT%\Reports\P0-05_final_acceptance.json"

echo ============================================================
echo CALL OF NARIS - P0-05 HERO PROMOTION + REGRESSION
echo ============================================================

for %%F in ("%UECMD%" "%UBT%" "%UAT%" "%UPROJECT%" "%PROMOTE%" "%ROLLBACK%" "%APPROVAL%") do (
  if not exist "%%~F" (
    echo [P0-05] FAIL missing: %%~F
    exit /b 70
  )
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$j=Get-Content -Raw -LiteralPath '%APPROVAL%'|ConvertFrom-Json;" ^
 "if($j.approved -ne $true){Write-Host '[P0-05] BLOCKED: visual approval is not true';exit 71};" ^
 "if($j.decision -notin @('APPROVE','APPROVED','PASS')){Write-Host '[P0-05] BLOCKED: visual decision invalid';exit 72};" ^
 "Write-Host ('[P0-05] Visual evidence accepted: '+$j.screenshot)"
if errorlevel 1 exit /b %errorlevel%

rem Remove old acceptance/promotion evidence before this attempt.
for %%F in ("%REPORT%" "%PROMOTION_REPORT%") do (
  if exist "%%~F" del /q "%%~F"
  if exist "%%~F" exit /b 74
)
echo [P0-05] Promoting candidate asset...
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%PROMOTE%" -stdout -FullStdOutLogOutput
if errorlevel 1 exit /b 73
powershell -NoProfile -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$p=Get-Content -Raw -LiteralPath '%PROMOTION_REPORT%'|ConvertFrom-Json;" ^
 "if($p.status -ne 'PASS' -or $p.promoted -ne $true -or $p.persisted -ne $true -or $p.active_path -ne '/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3'){exit 75}"
if errorlevel 1 exit /b 75

set "ComSpec=C:\Windows\System32\cmd.exe"
set "SHELL=%ComSpec%"

echo [P0-05] Building Win64 Development...
"%UBT%" NARIS Win64 Development -Project="%UPROJECT%" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 goto :rollback_build

echo [P0-05] Cleaning prior Cook / Stage / Archive outputs...
for %%D in ("%PROJECT%\Saved\Cooked\Windows" "%PROJECT%\Saved\StagedBuilds\Windows" "%ARCHIVE%\Windows") do (
  if exist "%%~D" (
    echo [P0-05] Removing %%~D
    rd /s /q "%%~D"
    if exist "%%~D" goto :rollback_clean
  )
)

echo [P0-05] Full Cook / Stage / Pak / Archive...
"%UAT%" BuildCookRun -project="%UPROJECT%" -noP4 -platform=Win64 -clientconfig=Development -skipbuild -cook -stage -pak -archive -archivedirectory="%ARCHIVE%" -map=/Game/NARIS/Maps/L_AshMap_Assembly -unattended -utf8output
if errorlevel 1 goto :rollback_package

if not exist "%PACKAGED%" goto :rollback_missing_package
if not exist "%PACKAGED_INTERNAL%" goto :rollback_missing_package
if exist "%QA_LOG%" del /q "%QA_LOG%"

echo [P0-05] Running packaged D3D12 combat regression on internal game binary...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$exe='%PACKAGED_INTERNAL%';" ^
 "$log='%QA_LOG%';" ^
 "$started=Get-Date;" ^
 "$p=Start-Process -FilePath $exe -ArgumentList @('-unattended','-nosplash','-windowed','-ResX=1280','-ResY=720','-d3d12','-NARISCOMBATQA',('-abslog='+$log)) -PassThru;" ^
 "if(-not $p.WaitForExit(120000)){try{$p.Kill()}catch{};exit 80};" ^
 "if($p.ExitCode -ne 0){exit $p.ExitCode};" ^
 "if(-not(Test-Path -LiteralPath $log)){exit 81};" ^
 "$fi=Get-Item -LiteralPath $log;" ^
 "if($fi.LastWriteTime -lt $started.AddSeconds(-2)){exit 85}"
if errorlevel 1 goto :rollback_runtime

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$l='%QA_LOG%';" ^
 "if(-not(Test-Path -LiteralPath $l)){exit 81};" ^
 "$txt=Get-Content -Raw -LiteralPath $l;" ^
 "if($txt -notmatch 'NARIS_COMBAT_QA_RESULT Pass=1'){exit 82};" ^
 "if($txt -match 'Fatal error|LowLevelFatalError|Unhandled Exception|Ensure condition failed|Assertion failed'){exit 83};" ^
 "if($txt -notmatch 'NARIS_HERO_VISUAL_QA MeshVisible=1'){exit 84};" ^
 "Write-Host '[P0-05] Packaged combat regression PASS'"
if errorlevel 1 goto :rollback_logqa

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$exe='%PACKAGED_INTERNAL%';$log='%QA_LOG%';$approval='%APPROVAL%';$promotion='%PROJECT%\Reports\P0-05_promotion.json';" ^
 "$a=Get-Content -Raw -LiteralPath $approval|ConvertFrom-Json;" ^
 "$o=[ordered]@{" ^
 " status='PASS';" ^
 " promoted=$true;" ^
 " packaged_combat_qa=$true;" ^
 " d3d12=$true;" ^
 " active_hero='/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3';" ^
 " rollback_asset='/Game/NARIS/Characters/HeroV3/Archive/SK_NARIS_AshenVessel_v3_PreP0';" ^
 " candidate_source_sha256=([string]$a.candidate_source_sha256).ToLowerInvariant();" ^
 " evidence_git_sha=[string]$a.evidence_git_sha;" ^
 " evidence_workflow_run_id=[string]$a.evidence_workflow_run_id;" ^
 " visual_approval_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $approval).Hash.ToLowerInvariant();" ^
 " promotion_report_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $promotion).Hash.ToLowerInvariant();" ^
 " packaged_internal=$exe;" ^
 " packaged_exe_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $exe).Hash.ToLowerInvariant();" ^
 " log=$log;" ^
 " qa_log_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $log).Hash.ToLowerInvariant();" ^
 " qa_log_bytes=(Get-Item -LiteralPath $log).Length;" ^
 " build='Win64 Development';" ^
 " package='Full Clean Cook/Stage/Pak/Archive';" ^
 "};" ^
 "[System.IO.File]::WriteAllText('%REPORT%',($o|ConvertTo-Json -Depth 6),[System.Text.UTF8Encoding]::new($false))"
if errorlevel 1 goto :rollback_report
echo ============================================================
echo [P0-05] PASS - PROMOTED HERO SURVIVED PACKAGED COMBAT QA
echo ============================================================
exit /b 0

:rollback_report
set "FAIL_REASON=acceptance_report_write_failed"
goto :rollback
:rollback_build
set "FAIL_REASON=win64_build_failed"
goto :rollback
:rollback_clean
set "FAIL_REASON=clean_cook_outputs_failed"
goto :rollback
:rollback_package
set "FAIL_REASON=package_failed"
goto :rollback
:rollback_missing_package
set "FAIL_REASON=packaged_exe_missing"
goto :rollback
:rollback_runtime
set "FAIL_REASON=packaged_runtime_failed"
goto :rollback
:rollback_logqa
set "FAIL_REASON=packaged_log_qa_failed"
goto :rollback

:rollback
echo [P0-05] FAILURE: !FAIL_REASON! - rolling back working HeroV3...
if exist "%ROLLBACK_REPORT%" del /q "%ROLLBACK_REPORT%"
if exist "%ROLLBACK_REPORT%" exit /b 99
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%ROLLBACK%" -stdout -FullStdOutLogOutput
set "RB=%ERRORLEVEL%"
if not "%RB%"=="0" exit /b 99
powershell -NoProfile -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$r=Get-Content -Raw -LiteralPath '%ROLLBACK_REPORT%'|ConvertFrom-Json;" ^
 "if($r.status -ne 'PASS' -or $r.rolled_back -ne $true -or $r.active_preserved -ne $true -or $r.persisted -ne $true){exit 99}"
if errorlevel 1 exit /b 99
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$o=[ordered]@{status='FAIL';promoted=$false;failure_reason='!FAIL_REASON!';rollback_exit_code=!RB!};" ^
 "[System.IO.File]::WriteAllText('%REPORT%',($o|ConvertTo-Json),[System.Text.UTF8Encoding]::new($false))"
if errorlevel 1 exit /b 98
if not "%RB%"=="0" (
  echo [P0-05] CRITICAL: rollback also failed.
  exit /b 99
)
echo [P0-05] Rollback PASS. Previous HeroV3 restored.
exit /b 90
