param([string]$EngineRoot="C:\Program Files\Epic Games\UE_5.7",[string]$RepoRoot=(Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path)
$ErrorActionPreference="Stop"
$Project=Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Editor=Join-Path $EngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$Content=Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python"
$steps=@(
 "naris_author_material_instances.py",
 "naris_stage33_bind_pbr_textures.py",
 "naris_stage33_bind_animation.py",
 "naris_stage30_validate_runtime_assets.py"
)
$env:NARIS_MATERIALS_STRICT="1"
foreach($s in $steps){
 $p=Join-Path $Content $s
 Write-Host "[Stage33] $s"
 & $Editor $Project "-ExecutePythonScript=$p" -unattended -nop4 -nosplash -NullRHI
 if($LASTEXITCODE -ne 0){throw "Stage33 failed at $s"}
}
Write-Host "Stage33 material + animation binding PASS"
