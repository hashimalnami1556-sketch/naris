param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [Parameter(Mandatory=$true)][string]$BlendFile,
    [Parameter(Mandatory=$true)][string]$AssetId,
    [string]$BlenderExe = $env:BLENDER_EXE,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT
)

$ErrorActionPreference = "Stop"

if (-not $BlenderExe) {
    $candidates = @(
        "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
    )
    $BlenderExe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) {
    throw "Blender executable not found. Set BLENDER_EXE."
}
if (-not (Test-Path $BlendFile)) {
    throw "Blend file not found: $BlendFile"
}
if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

$BlenderScript = Join-Path $RepoRoot "tools\blender\naris_export.py"
$UnrealScript = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_import_blender_exchange.py"
$UProject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Registry = Join-Path $RepoRoot "data\MASTER_ASSET_REGISTRY.json"
$UnrealCmd = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$OutDir = Join-Path $RepoRoot "artifacts\local\blender\$AssetId"
$Manifest = Join-Path $OutDir ($AssetId + "_blender_manifest.json")

foreach ($path in @($BlenderScript, $UnrealScript, $UProject, $Registry, $UnrealCmd)) {
    if (-not (Test-Path $path)) { throw "Required path missing: $path" }
}

$registryData = Get-Content $Registry -Raw | ConvertFrom-Json
$registryMatches = @($registryData.assets | Where-Object { $_.id -eq $AssetId })
if ($registryMatches.Count -ne 1) {
    throw "Asset ID must appear exactly once in master registry: $AssetId"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "[NARIS] Blender validation/export: $AssetId"
& $BlenderExe --background $BlendFile --python $BlenderScript -- --out $OutDir --asset-id $AssetId --registry $Registry
if ($LASTEXITCODE -ne 0) { throw "Blender validation/export failed with exit code $LASTEXITCODE" }
if (-not (Test-Path $Manifest)) { throw "Expected manifest was not produced: $Manifest" }

$env:NARIS_EXCHANGE_MANIFEST = $Manifest
$env:NARIS_MASTER_REGISTRY = $Registry
Write-Host "[NARIS] Unreal import smoke test: $Manifest"
& $UnrealCmd $UProject "-ExecutePythonScript=$UnrealScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) { throw "Unreal import smoke test failed with exit code $LASTEXITCODE" }

Write-Host "[NARIS] Blender -> Unreal smoke test PASSED for $AssetId"
