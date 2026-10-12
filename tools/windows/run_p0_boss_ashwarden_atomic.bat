@echo off
setlocal EnableExtensions
set "BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set "UECMD=C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "OUT=%PROJECT%\Production\Boss\AshWarden"

set "BOSS01=%~dp0..\blender\p0_boss_ashwarden_oneshot.py"
set "BOSS02=%~dp0..\blender\p0_boss_02_rig_anim_pbr.py"
set "BOSS03=%~dp0..\unreal\p0_boss_03_import_qa.py"

set "REPORT01=%OUT%\P0-BOSS_AshWarden_log.json"
set "REPORT02=%OUT%\P0-BOSS-02_rig_anim_pbr.json"
set "REPORT03=%PROJECT%\Reports\P0-BOSS-03_unreal_qa.json"

echo ============================================================
echo CALL OF NARIS - ASH WARDEN ATOMIC PRODUCTION CANDIDATE
echo P0-BOSS-01 -> P0-BOSS-02 -> P0-BOSS-03
echo ============================================================

for %%F in ("%BLENDER%" "%UECMD%" "%UPROJECT%" "%BOSS01%" "%BOSS02%" "%BOSS03%") do (
  if not exist "%%~F" (
    echo [ASH-WARDEN] FAIL missing: %%~F
    exit /b 120
  )
)
if not exist "%OUT%" mkdir "%OUT%"

echo.
echo [1/3] Scan / score / build unique candidate...
"%BLENDER%" -b -P "%BOSS01%" -- --out "%OUT%"
if errorlevel 1 exit /b 121
if not exist "%REPORT01%" exit /b 122
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT01%'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS_CANDIDATE'){exit 123};" ^
 "Write-Host ('[ASH-WARDEN] BOSS-01 candidate='+$j.candidate_type);" ^
 "Write-Host ('[ASH-WARDEN] procedural_fallback='+$j.used_procedural_fallback)"
if errorlevel 1 exit /b 123

echo.
echo [2/3] Canonical rig / six animations / PBR gate...
"%BLENDER%" -b -P "%BOSS02%" -- --boss-dir "%OUT%"
if errorlevel 1 exit /b 130
if not exist "%REPORT02%" exit /b 131
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT02%'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS' -or $j.production_candidate -ne $true){exit 132};" ^
 "if($j.actions.Count -lt 6){exit 133};" ^
 "Write-Host ('[ASH-WARDEN] BOSS-02 bones='+$j.bone_count+' height='+$j.body_height_m);" ^
 "Write-Host ('[ASH-WARDEN] animations='+($j.actions.name -join ','))"
if errorlevel 1 exit /b %errorlevel%

echo.
echo [3/3] Unreal import / PhysicsAsset / LOD / animation / QA arena...
if exist "%REPORT03%" del /q "%REPORT03%"
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%BOSS03%" -stdout -FullStdOutLogOutput
if errorlevel 1 exit /b 140
if not exist "%REPORT03%" exit /b 141
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT03%'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS'){exit 142};" ^
 "if($j.candidate_only -ne $true -or $j.replacement_allowed -ne $false){exit 143};" ^
 "if($j.technical_acceptance -ne $true){exit 144};" ^
 "Write-Host ('[ASH-WARDEN] BOSS-03 asset='+$j.asset);" ^
 "Write-Host ('[ASH-WARDEN] lods='+$j.lod_count);" ^
 "Write-Host ('[ASH-WARDEN] qa_map='+$j.qa_map);" ^
 "Write-Host ('[ASH-WARDEN] screenshot='+$j.screenshot_target)"
if errorlevel 1 exit /b %errorlevel%

echo.
echo ============================================================
echo [ASH-WARDEN] PASS THROUGH P0-BOSS-03 TECHNICAL/SCENE GATE
echo Candidate is NOT active gameplay art yet.
echo P0-BOSS-04 remains BLOCKED until rendered D3D12 boss QA passes.
echo ============================================================
exit /b 0
