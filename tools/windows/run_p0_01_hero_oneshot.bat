@echo off
setlocal EnableExtensions
set "BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "SCRIPT=%PROJECT%\Tools\Blender\p0_01_hero_oneshot.py"
set "OUT=%PROJECT%\Production\Hero"

if not exist "%BLENDER%" (
  echo [P0-01] FAIL: Blender 5.2 not found: %BLENDER%
  exit /b 10
)
if not exist "%SCRIPT%" (
  echo [P0-01] FAIL: Script not found: %SCRIPT%
  exit /b 11
)

if not exist "%OUT%" mkdir "%OUT%"

echo [P0-01] CALL OF NARIS Hero Atomic Production Pass
echo [P0-01] Blender: %BLENDER%
echo [P0-01] Script : %SCRIPT%
echo [P0-01] Output : %OUT%

"%BLENDER%" -b -P "%SCRIPT%" -- --out "%OUT%"
set "CODE=%ERRORLEVEL%"

echo.
echo [P0-01] Blender exit code: %CODE%
if not "%CODE%"=="0" exit /b %CODE%

if not exist "%OUT%\P0-01_reimport_log.json" (
  echo [P0-01] FAIL: Missing P0-01_reimport_log.json
  exit /b 12
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p='%OUT%\P0-01_reimport_log.json';" ^
  "$j=Get-Content -Raw -LiteralPath $p | ConvertFrom-Json;" ^
  "Write-Host ('[P0-01] STATUS=' + $j.status);" ^
  "Write-Host ('[P0-01] PRODUCTION_GRADE=' + $j.production_grade);" ^
  "Write-Host ('[P0-01] WINNER=' + $j.winner.path);" ^
  "Write-Host ('[P0-01] SCORE=' + $j.winner.score);" ^
  "if($j.production_grade -ne $true){exit 13}"

if errorlevel 1 (
  echo [P0-01] FAIL: Output exists but did not pass Production gate.
  exit /b 13
)

echo [P0-01] PASS: Production hero accepted.
exit /b 0
