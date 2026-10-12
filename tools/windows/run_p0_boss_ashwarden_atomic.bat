@echo off
setlocal EnableExtensions
set "BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set "UECMD=C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
set "PROJECT=C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
set "UPROJECT=%PROJECT%\NARIS.uproject"
set "OUT=%PROJECT%\Production\Boss\AshWarden"
set "BOSS01=%~dp0..\blender\p0_boss_ashwarden_oneshot.py"
set "BOSS02=%~dp0..\unreal\p0_boss_02_import_ashwarden.py"
set "REPORT=%PROJECT%\Reports\P0-BOSS-02_unreal_import.json"

echo ============================================================
echo CALL OF NARIS - ASH WARDEN ATOMIC CANDIDATE PIPELINE
echo Blender Candidate -> Unreal Candidate Import
echo ============================================================

for %%F in ("%BLENDER%" "%UECMD%" "%UPROJECT%" "%BOSS01%" "%BOSS02%") do (
  if not exist "%%~F" (
    echo [ASH-WARDEN] FAIL missing: %%~F
    exit /b 120
  )
)
if not exist "%OUT%" mkdir "%OUT%"

echo [1/2] Building/scoring unique Ash Warden candidate...
"%BLENDER%" -b -P "%BOSS01%" -- --out "%OUT%"
if errorlevel 1 exit /b 121

if not exist "%OUT%\P0-BOSS_AshWarden_log.json" exit /b 122
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%OUT%\P0-BOSS_AshWarden_log.json'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS_CANDIDATE'){exit 123};" ^
 "Write-Host ('[ASH-WARDEN] Blender candidate='+$j.candidate_type)"
if errorlevel 1 exit /b 123

echo [2/2] Importing candidate to Unreal...
if exist "%REPORT%" del /q "%REPORT%"
"%UECMD%" "%UPROJECT%" -unattended -nop4 -nosplash -ExecutePythonScript="%BOSS02%" -stdout -FullStdOutLogOutput
if errorlevel 1 exit /b 124

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$j=Get-Content -Raw -LiteralPath '%REPORT%'|ConvertFrom-Json;" ^
 "if($j.status -ne 'PASS'){exit 125};" ^
 "if($j.candidate_only -ne $true){exit 126};" ^
 "Write-Host ('[ASH-WARDEN] Unreal candidate='+$j.asset);" ^
 "Write-Host ('[ASH-WARDEN] NEXT='+$j.next_gate)"
if errorlevel 1 exit /b %errorlevel%

echo ============================================================
echo [ASH-WARDEN] PASS CANDIDATE ONLY
echo Current gameplay boss proxy remains unchanged until D3D12 QA.
echo ============================================================
exit /b 0
