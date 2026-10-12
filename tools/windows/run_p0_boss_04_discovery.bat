@echo off
setlocal EnableExtensions

set "UECMD=C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "SCRIPT=%~dp0..\unreal\p0_boss_04_discover_integration.py"
set "REPORT=%PROJECT%\Reports\P0-BOSS-04_integration_discovery.json"

echo ============================================================
echo CALL OF NARIS - ASH WARDEN P0-BOSS-04 INTEGRATION DISCOVERY
echo READ ONLY - NO GAMEPLAY ASSET REPLACEMENT
echo ============================================================

for %%F in ("%UECMD%" "%UPROJECT%" "%SCRIPT%") do (
  if not exist "%%~F" (
    echo [BOSS-DISCOVERY] FAIL missing: %%~F
    exit /b 220
  )
)

if exist "%REPORT%" del /q "%REPORT%"
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%SCRIPT%" -stdout -FullStdOutLogOutput
if errorlevel 1 exit /b 221
if not exist "%REPORT%" exit /b 222

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT%'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS'){exit 223};" ^
 "if($j.read_only -ne $true -or $j.replacement_allowed -ne $false){exit 224};" ^
 "Write-Host ('[BOSS-DISCOVERY] MAP='+$j.map);" ^
 "Write-Host ('[BOSS-DISCOVERY] TARGET='+$j.target.class+' / '+$j.target.label);" ^
 "Write-Host ('[BOSS-DISCOVERY] PROXY='+($j.current_proxy_meshes -join ','));" ^
 "Write-Host ('[BOSS-DISCOVERY] BONEBEAST_PROXY='+$j.bonebeast_proxy_confirmed);" ^
 "Write-Host ('[BOSS-DISCOVERY] NATIVE_COMPONENT='+$j.native_skeletal_component);" ^
 "Write-Host ('[BOSS-DISCOVERY] STRATEGY='+$j.recommended_integration_strategy)"
if errorlevel 1 exit /b %errorlevel%

echo ============================================================
echo [BOSS-DISCOVERY] PASS READ-ONLY DISCOVERY
echo P0-BOSS-04 promotion remains BLOCKED until this report and
echo local NarisAshWarden ownership are verified.
echo ============================================================
exit /b 0
