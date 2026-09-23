param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT
)

$ErrorActionPreference = "Stop"

if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

$UProject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Script = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_bootstrap_w04_smoke.py"
$AnimationValidationScript = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_validate_animation_bindings.py"
$ProductionAssetValidationScript = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_validate_production_assets.py"
$MaterialAuthoringScript = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_author_material_instances.py"
$MaterialValidationScript = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_validate_material_bindings.py"
$AudioImportScript = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_import_presentation_audio.py"
$PresentationResolver = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_resolve_presentation_bindings.py"
$PresentationScript = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_build_presentation_profile.py"
$UnrealCmd = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

foreach ($path in @($UProject, $Script, $AnimationValidationScript, $ProductionAssetValidationScript, $MaterialAuthoringScript, $MaterialValidationScript, $AudioImportScript, $PresentationResolver, $PresentationScript, $UnrealCmd)) {
    if (-not (Test-Path $path)) {
        throw "Required path missing: $path"
    }
}

Write-Host "[NARIS] Creating/loading W04_Prototype editor smoke map"
& $UnrealCmd $UProject "-ExecutePythonScript=$Script" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 editor bootstrap failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Validating production animation bindings and notifies"
& $UnrealCmd $UProject "-ExecutePythonScript=$AnimationValidationScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 animation validation failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Validating core production meshes/materials/LOD/collision"
& $UnrealCmd $UProject "-ExecutePythonScript=$ProductionAssetValidationScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 production asset validation failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Authoring W04 material instances from approved master materials"
& $UnrealCmd $UProject "-ExecutePythonScript=$MaterialAuthoringScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 material instance authoring failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Validating W04 master/material-instance PBR bindings"
& $UnrealCmd $UProject "-ExecutePythonScript=$MaterialValidationScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 material validation failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Importing validated presentation WAV sources"
& $UnrealCmd $UProject "-ExecutePythonScript=$AudioImportScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 presentation audio import failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Resolving real presentation payloads at deterministic paths"
& $UnrealCmd $UProject "-ExecutePythonScript=$PresentationResolver" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 presentation binding resolution failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Building/loading shared W04 presentation profile"
& $UnrealCmd $UProject "-ExecutePythonScript=$PresentationScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 presentation authoring failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] W04 editor bootstrap completed"
