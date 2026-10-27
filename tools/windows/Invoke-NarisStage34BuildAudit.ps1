param(
 [Parameter(Mandatory=$true)][string]$RepoRoot,
 [Parameter(Mandatory=$true)][string]$UnrealEngineRoot
)
$ErrorActionPreference='Stop'
$Project=Join-Path $RepoRoot 'unreal/NARIS_W04/NARIS_W04.uproject'
$Build=Join-Path $UnrealEngineRoot 'Engine/Build/BatchFiles/Build.bat'
$EditorCmd=Join-Path $UnrealEngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$Audit=Join-Path $RepoRoot 'unreal/NARIS_W04/Content/Python/naris_stage34_anim_material_audit.py'
foreach($file in @($Project,$Build,$EditorCmd,$Audit)){if(!(Test-Path -LiteralPath $file)){throw "Missing required file: $file"}}
& $Build NARIS_W04Editor Win64 Development "-Project=$Project" -WaitMutex
if($LASTEXITCODE -ne 0){throw "Unreal C++ build failed with code $LASTEXITCODE"}
& $EditorCmd $Project -unattended -nop4 -nosplash -nullrhi "-run=pythonscript" "-script=$Audit"
if($LASTEXITCODE -ne 0){throw "Stage34 asset audit failed with code $LASTEXITCODE"}
Write-Host 'PASS: Editor compile and asset presence audit. PIE gameplay still requires a separate runtime test.'
