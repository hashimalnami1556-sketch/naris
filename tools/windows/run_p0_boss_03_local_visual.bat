@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ENGINE=C:\Program Files\Epic Games\UE_5.7\Engine"
set "UEGUI=%ENGINE%\Binaries\Win64\UnrealEditor.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "PIPELINE=%~dp0run_p0_boss_ashwarden_atomic.bat"
set "SCREEN_DIR=%PROJECT%\Saved\Screenshots\Windows"
set "SCENE_REPORT=%PROJECT%\Reports\P0-BOSS-03_unreal_qa.json"
set "EVIDENCE=%PROJECT%\Reports\P0-BOSS-03_render_evidence.json"
set "SHOT=%SCREEN_DIR%\P0-BOSS-03_AshWardenCompare.png"
set "REVISION=p0-boss-03-ashwarden-visual-v1"
set "STAMP_FILE=%TEMP%\naris_boss_render_start.txt"

echo ============================================================
echo CALL OF NARIS - ASH WARDEN LOCAL D3D12 EVIDENCE PIPELINE
echo P0-BOSS-01 -> 02 -> 03 -> Render Evidence
echo ============================================================

for %%F in ("%UEGUI%" "%UPROJECT%" "%PIPELINE%") do (
  if not exist "%%~F" (
    echo [ASH-WARDEN-VISUAL] FAIL missing: %%~F
    exit /b 200
  )
)

call "%PIPELINE%"
if errorlevel 1 (
  echo [ASH-WARDEN-VISUAL] STOP: atomic boss pipeline failed.
  exit /b 201
)

if not exist "%SCENE_REPORT%" (
  echo [ASH-WARDEN-VISUAL] FAIL: missing P0-BOSS-03 report.
  exit /b 202
)

if not exist "%SCREEN_DIR%" mkdir "%SCREEN_DIR%"
del /q "%SCREEN_DIR%\*.png" 2>nul
powershell -NoProfile -Command "(Get-Date).ToUniversalTime().ToString('o')" > "%STAMP_FILE%"
set /p RENDER_START=<"%STAMP_FILE%"
del /q "%STAMP_FILE%" 2>nul

echo [ASH-WARDEN-VISUAL] Rendering D3D12 boss comparison...
"%UEGUI%" "%UPROJECT%" /Game/NARIS/QA/L_AshWardenCandidate_QA -game -d3d12 -windowed -ResX=1920 -ResY=1080 -nosplash -BENCHMARK -SECONDS=12 -ExecCmds="HighResShot 1" -log
if errorlevel 1 (
  echo [ASH-WARDEN-VISUAL] FAIL: D3D12 boss QA run failed.
  exit /b 203
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$dir='%SCREEN_DIR%';" ^
 "$canonical='%SHOT%';" ^
 "$started=[DateTimeOffset]::Parse('%RENDER_START%').UtcDateTime;" ^
 "$latest=Get-ChildItem -LiteralPath $dir -Filter '*.png'|Where-Object {$_.LastWriteTimeUtc -ge $started}|Sort-Object LastWriteTimeUtc -Descending|Select-Object -First 1;" ^
 "if(-not $latest){throw 'No fresh Ash Warden screenshot produced after render start'};" ^
 "if($latest.FullName -ne $canonical){Copy-Item -LiteralPath $latest.FullName -Destination $canonical -Force};" ^
 "$scene=Get-Content -Raw -LiteralPath '%SCENE_REPORT%'|ConvertFrom-Json;" ^
 "$hash=(Get-FileHash -LiteralPath $canonical -Algorithm SHA256).Hash.ToLowerInvariant();" ^
 "$bytes=(Get-Item -LiteralPath $canonical).Length;" ^
 "$stamp=(Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ');" ^
 "$repoRoot=(Resolve-Path (Join-Path '%~dp0' '..\..')).Path;" ^
 "$gitSha=(& git -C $repoRoot rev-parse HEAD 2>$null).Trim();" ^
 "if(-not $gitSha){throw 'Unable to resolve Git HEAD for boss visual evidence'};" ^
 "$dirty=((& git -C $repoRoot status --porcelain 2>$null) -join '').Trim().Length -gt 0;" ^
 "$e=[ordered]@{" ^
 " schema_version='1.0.0';" ^
 " pipeline_revision='%REVISION%';" ^
 " status='PASS';" ^
 " screenshot='P0-BOSS-03_AshWardenCompare.png';" ^
 " screenshot_path=$canonical;" ^
 " screenshot_sha256=$hash;" ^
 " screenshot_bytes=$bytes;" ^
 " candidate=$scene.asset;" ^
 " baseline_proxy=$scene.baseline_proxy;" ^
 " qa_map=$scene.qa_map;" ^
 " animations=$scene.animations;" ^
 " git_sha=$gitSha;" ^
 " git_worktree_dirty=$dirty;" ^
 " render_started_utc='%RENDER_START%';" ^
 " screenshot_written_utc=$latest.LastWriteTimeUtc.ToString('o');" ^
 " workflow_run_id=('local-boss-'+$stamp);" ^
 "};" ^
 "$e|ConvertTo-Json -Depth 8|Set-Content -Encoding utf8NoBOM -LiteralPath '%EVIDENCE%';" ^
 "Write-Host ('[ASH-WARDEN-VISUAL] SCREENSHOT='+$canonical);" ^
 "Write-Host ('[ASH-WARDEN-VISUAL] SHA256='+$hash);" ^
 "Write-Host ('[ASH-WARDEN-VISUAL] BYTES='+$bytes);" ^
 "Write-Host ('[ASH-WARDEN-VISUAL] GIT_SHA='+$gitSha);" ^
 "Write-Host ('[ASH-WARDEN-VISUAL] DIRTY='+$dirty)"
if errorlevel 1 (
  echo [ASH-WARDEN-VISUAL] FAIL: evidence generation failed.
  exit /b 204
)

echo.
echo ============================================================
echo [ASH-WARDEN-VISUAL] PASS EVIDENCE GENERATED
echo Evidence: %EVIDENCE%
echo Screenshot: %SHOT%
echo IMPORTANT: P0-BOSS-04 replacement remains BLOCKED until
echo rendered visual criteria and local NarisAshWarden integration are verified.
echo ============================================================
exit /b 0
