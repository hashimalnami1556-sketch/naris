@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ENGINE=C:\Program Files\Epic Games\UE_5.7\Engine"
set "UEGUI=%ENGINE%\Binaries\Win64\UnrealEditor.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "PIPELINE=%~dp0run_p0_hero_to_unreal.bat"
set "SCREEN_DIR=%PROJECT%\Saved\Screenshots\Windows"
set "SCENE_REPORT=%PROJECT%\Reports\P0-04B_visual_scene.json"
set "EVIDENCE=%PROJECT%\Reports\P0-04B_render_evidence.json"
set "SHOT=%SCREEN_DIR%\P0-04B_HeroCompare.png"
set "REVISION=p0-04b-hashbound-camera-v2"

echo ============================================================
echo CALL OF NARIS - LOCAL ATOMIC HERO PIPELINE
echo P0-01 -> P0-02 -> P0-03 -> P0-04A -> P0-04B Render Evidence
echo ============================================================

for %%F in ("%UEGUI%" "%UPROJECT%" "%PIPELINE%") do (
  if not exist "%%~F" (
    echo [LOCAL-P0] FAIL missing: %%~F
    exit /b 100
  )
)

call "%PIPELINE%"
if errorlevel 1 (
  echo [LOCAL-P0] STOP: source-to-Unreal pipeline failed.
  exit /b 101
)

if not exist "%SCENE_REPORT%" (
  echo [LOCAL-P0] FAIL: missing P0-04B scene report.
  exit /b 102
)

if not exist "%SCREEN_DIR%" mkdir "%SCREEN_DIR%"
if exist "%SHOT%" del /q "%SHOT%"

echo [LOCAL-P0] Rendering D3D12 comparison screenshot...
"%UEGUI%" "%UPROJECT%" /Game/NARIS/QA/L_HeroCandidate_QA -game -d3d12 -windowed -ResX=1920 -ResY=1080 -nosplash -BENCHMARK -SECONDS=10 -ExecCmds="HighResShot 1" -log
if errorlevel 1 (
  echo [LOCAL-P0] FAIL: D3D12 comparison run failed.
  exit /b 103
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$dir='%SCREEN_DIR%';" ^
 "$canonical='%SHOT%';" ^
 "$latest=Get-ChildItem -LiteralPath $dir -Filter '*.png'|Sort-Object LastWriteTime -Descending|Select-Object -First 1;" ^
 "if(-not $latest){throw 'No screenshot produced'};" ^
 "if($latest.FullName -ne $canonical){Copy-Item -LiteralPath $latest.FullName -Destination $canonical -Force};" ^
 "$scene=Get-Content -Raw -LiteralPath '%SCENE_REPORT%'|ConvertFrom-Json;" ^
 "$hash=(Get-FileHash -LiteralPath $canonical -Algorithm SHA256).Hash.ToLowerInvariant();" ^
 "$bytes=(Get-Item -LiteralPath $canonical).Length;" ^
 "$stamp=(Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ');" ^
 "$e=[ordered]@{" ^
 " schema_version='1.0.0';" ^
 " pipeline_revision='%REVISION%';" ^
 " status='PASS';" ^
 " screenshot='P0-04B_HeroCompare.png';" ^
 " screenshot_path=$canonical;" ^
 " screenshot_sha256=$hash;" ^
 " screenshot_bytes=$bytes;" ^
 " candidate=$scene.candidate;" ^
 " baseline=$scene.baseline;" ^
 " qa_map=$scene.qa_map;" ^
 " git_sha='LOCAL_WORKTREE';" ^
 " workflow_run_id=('local-'+$stamp);" ^
 "};" ^
 "$e|ConvertTo-Json -Depth 6|Set-Content -Encoding utf8NoBOM -LiteralPath '%EVIDENCE%';" ^
 "Write-Host ('[LOCAL-P0] SCREENSHOT='+$canonical);" ^
 "Write-Host ('[LOCAL-P0] SHA256='+$hash);" ^
 "Write-Host ('[LOCAL-P0] BYTES='+$bytes)"
if errorlevel 1 (
  echo [LOCAL-P0] FAIL: render evidence generation failed.
  exit /b 104
)

echo.
echo ============================================================
echo [LOCAL-P0] PASS THROUGH P0-04B EVIDENCE GENERATION
echo Evidence: %EVIDENCE%
echo Screenshot: %SHOT%
echo IMPORTANT: P0-05 promotion remains BLOCKED until visual approval
echo is explicitly written with this exact hash/candidate/revision.
echo ============================================================
exit /b 0
