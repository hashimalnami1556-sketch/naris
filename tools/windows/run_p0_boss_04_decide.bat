@echo off
setlocal EnableExtensions

set "PYTHON=python"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "SCRIPT=%~dp0..\ci\p0_boss_04_decide_promotion.py"
set "REPORT=%PROJECT%\Reports\P0-BOSS-04_decision.json"
set "REPO=%~dp0..\.."

echo ============================================================
echo CALL OF NARIS - ASH WARDEN P0-BOSS-04 DECISION GATE
echo READ ONLY - DECIDES STRATEGY, DOES NOT PROMOTE
echo ============================================================

if not exist "%SCRIPT%" (
  echo [BOSS-DECISION] FAIL missing: %SCRIPT%
  exit /b 230
)
if not exist "%PROJECT%" (
  echo [BOSS-DECISION] FAIL project missing: %PROJECT%
  exit /b 231
)

if exist "%REPORT%" del /q "%REPORT%"

%PYTHON% "%SCRIPT%" --project-root "%PROJECT%" --repo-root "%REPO%"
set "CODE=%ERRORLEVEL%"

if not exist "%REPORT%" (
  echo [BOSS-DECISION] FAIL no decision report generated.
  exit /b 232
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT%'|ConvertFrom-Json;" ^
 "Write-Host ('[BOSS-DECISION] STATUS='+$j.status);" ^
 "Write-Host ('[BOSS-DECISION] DECISION='+$j.decision);" ^
 "Write-Host ('[BOSS-DECISION] TARGET='+$j.integration_target.class+' / '+$j.integration_target.label);" ^
 "Write-Host ('[BOSS-DECISION] PROXY='+($j.current_proxy_meshes -join ','));" ^
 "Write-Host ('[BOSS-DECISION] STRATEGY='+$j.recommended_integration_strategy);" ^
 "Write-Host ('[BOSS-DECISION] REPLACEMENT_ALLOWED='+$j.replacement_allowed)"

if "%CODE%"=="0" (
  echo [BOSS-DECISION] READY: reversible instance/Blueprint promotion may be authored.
  exit /b 0
)

echo [BOSS-DECISION] BLOCKED with code %CODE%.
echo No gameplay asset was changed.
exit /b %CODE%
