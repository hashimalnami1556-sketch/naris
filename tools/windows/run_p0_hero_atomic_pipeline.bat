@echo off
setlocal EnableExtensions
set "BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "HERO_DIR=%PROJECT%\Production\Hero"
set "P001=%~dp0..\blender\p0_01_hero_oneshot.py"
set "P002=%~dp0..\blender\p0_02_hero_rig_pbr.py"

echo ============================================================
echo CALL OF NARIS - HERO PRODUCTION ATOMIC PIPELINE
echo P0-01 Scan/Score/Select  ->  P0-02 Rig/PBR Gate
echo ============================================================

if not exist "%BLENDER%" (
  echo [PIPELINE] FAIL 10: Blender 5.2 missing
  exit /b 10
)
if not exist "%P001%" (
  echo [PIPELINE] FAIL 11: P0-01 missing
  exit /b 11
)
if not exist "%P002%" (
  echo [PIPELINE] FAIL 12: P0-02 missing
  exit /b 12
)
if not exist "%HERO_DIR%" mkdir "%HERO_DIR%"

echo.
echo [PIPELINE] Phase P0-01...
"%BLENDER%" -b -P "%P001%" -- --out "%HERO_DIR%"
if errorlevel 1 (
  echo [PIPELINE] STOP: P0-01 failed.
  exit /b 21
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%HERO_DIR%\P0-01_reimport_log.json'|ConvertFrom-Json;" ^
 "if($j.production_grade -ne $true){Write-Host '[PIPELINE] STOP: P0-01 produced emergency/non-production asset'; exit 22};" ^
 "Write-Host ('[PIPELINE] P0-01 accepted: '+$j.winner.path+' score='+$j.winner.score)"
if errorlevel 1 exit /b 22

echo.
echo [PIPELINE] Phase P0-02...
"%BLENDER%" -b -P "%P002%" -- --hero-dir "%HERO_DIR%"
if errorlevel 1 (
  echo [PIPELINE] STOP: P0-02 Rig/PBR gate failed.
  exit /b 30
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%HERO_DIR%\P0-02_rig_pbr_log.json'|ConvertFrom-Json;" ^
 "if($j.production_grade -ne $true){exit 31};" ^
 "Write-Host ('[PIPELINE] FINAL HERO='+$j.output_fbx);" ^
 "Write-Host ('[PIPELINE] BONES='+$j.bone_count+' HEIGHT='+$j.height_m+'m');" ^
 "Write-Host ('[PIPELINE] CANONICAL='+($j.canonical_present -join ','))"
if errorlevel 1 exit /b 31

echo.
echo ============================================================
echo [PIPELINE] PASS: P0 HERO READY FOR UNREAL IMPORT
echo %HERO_DIR%\SK_AshenVessel_PBR.fbx
echo ============================================================
exit /b 0
