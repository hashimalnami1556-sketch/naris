@echo off
setlocal EnableExtensions
set "BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set "UECMD=C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "HERO_DIR=%PROJECT%\Production\Hero"
set "P001=%~dp0..\blender\p0_01_hero_oneshot.py"
set "P002=%~dp0..\blender\p0_02_hero_rig_pbr.py"
set "P003=%~dp0..\unreal\p0_03_import_hero.py"
set "P004A=%~dp0..\unreal\p0_04a_hero_technical_qa.py"
set "REPORT3=%PROJECT%\Reports\P0-03_unreal_hero_import.json"
set "REPORT4A=%PROJECT%\Reports\P0-04A_hero_technical_qa.json"

echo ============================================================
echo CALL OF NARIS - HERO SOURCE TO UNREAL ATOMIC PIPELINE
echo P0-01 -> P0-02 -> P0-03 -> P0-04A
echo ============================================================

if not exist "%BLENDER%" exit /b 10
if not exist "%UECMD%" exit /b 11
if not exist "%UPROJECT%" exit /b 12
if not exist "%P001%" exit /b 13
if not exist "%P002%" exit /b 14
if not exist "%P003%" exit /b 15
if not exist "%P004A%" exit /b 16
if not exist "%HERO_DIR%" mkdir "%HERO_DIR%"

echo [1/4] P0-01 Scan Score Select Rebuild...
"%BLENDER%" -b -P "%P001%" -- --out "%HERO_DIR%"
if errorlevel 1 exit /b 21

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%HERO_DIR%\P0-01_reimport_log.json'|ConvertFrom-Json;" ^
 "if($j.production_grade -ne $true){exit 22};" ^
 "Write-Host ('P0-01 PASS winner='+$j.winner.path+' score='+$j.winner.score)"
if errorlevel 1 exit /b 22

echo [2/4] P0-02 Rig Canonicalization PBR Gate...
"%BLENDER%" -b -P "%P002%" -- --hero-dir "%HERO_DIR%"
if errorlevel 1 exit /b 30

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%HERO_DIR%\P0-02_rig_pbr_log.json'|ConvertFrom-Json;" ^
 "if($j.production_grade -ne $true){exit 31};" ^
 "Write-Host ('P0-02 PASS bones='+$j.bone_count+' height='+$j.height_m)"
if errorlevel 1 exit /b 31

echo [3/4] P0-03 Unreal Candidate Import...
if exist "%REPORT3%" del /q "%REPORT3%"
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%P003%" -stdout -FullStdOutLogOutput
if errorlevel 1 exit /b 40

if not exist "%REPORT3%" exit /b 41
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT3%'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS'){exit 42};" ^
 "Write-Host ('P0-03 PASS mesh='+$j.skeletal_mesh);" ^
 "Write-Host ('NEXT='+$j.next_gate)"
if errorlevel 1 exit /b 42

echo [4/4] P0-04A Technical QA...
if exist "%REPORT4A%" del /q "%REPORT4A%"
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%P004A%" -stdout -FullStdOutLogOutput
if errorlevel 1 exit /b 50

if not exist "%REPORT4A%" exit /b 51
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT4A%'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS' -or $j.technical_acceptance -ne $true){exit 52};" ^
 "Write-Host ('P0-04A PASS candidate='+$j.candidate);" ^
 "Write-Host ('NEXT='+$j.next_gate)"
if errorlevel 1 exit /b 52

echo ============================================================
echo HERO CANDIDATE TECHNICALLY READY IN UNREAL.
echo IMPORTANT: Candidate has NOT replaced working HeroV3 yet.
echo Replacement remains BLOCKED until P0-04B D3D12 visual+combat QA.
echo ============================================================
exit /b 0
