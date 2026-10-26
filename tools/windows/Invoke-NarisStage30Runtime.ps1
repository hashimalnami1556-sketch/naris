param(
 [string]$EngineRoot="C:\Program Files\Epic Games\UE_5.7",
 [string]$RepoRoot=(Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)
$ErrorActionPreference="Stop"
$Project=Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Editor=Join-Path $EngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$UBT=Join-Path $EngineRoot "Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
$Validator=Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_stage30_validate_runtime_assets.py"
if(!(Test-Path $Project)){throw "Missing uproject"}
if(!(Test-Path $Editor)){throw "UE 5.7 editor commandlet missing"}
if(!(Test-Path $UBT)){throw "UnrealBuildTool missing"}
Write-Host "[1/4] C++ Development Editor build"
& $UBT NARIS_W04Editor Win64 Development "-Project=$Project" -WaitMutex -NoHotReload
if($LASTEXITCODE -ne 0){throw "C++ build failed"}
Write-Host "[2/4] Animation/PBR asset gate"
& $Editor $Project -ExecutePythonScript="$Validator" -unattended -nop4 -nosplash -NullRHI
if($LASTEXITCODE -ne 0){throw "Animation/PBR gate failed"}
Write-Host "[3/4] Final map load commandlet"
& $Editor $Project "/Game/NARIS/W04/Maps/W04_AshenForest" -run=NarisValidateShippingMap -unattended -nop4 -nosplash -NullRHI
if($LASTEXITCODE -ne 0){throw "Final map validation failed"}
Write-Host "[4/4] Stage30 PASS: repository + UE5.7 compile/assets/map gates"
Write-Host "Interactive PIE combat remains a human/runtime evidence gate."
