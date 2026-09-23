param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
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
if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

$AssetId = "NARIS-W04-ENV-FACTORY-0002"
$Factory = Join-Path $RepoRoot "tools\blender\NARIS_W04_ASHEN_FOREST_FACTORY_v2.py"
$Bridge = Join-Path $RepoRoot "tools\windows\Invoke-NarisBlenderUnrealSmoke.ps1"
$Registry = Join-Path $RepoRoot "data\MASTER_ASSET_REGISTRY.json"
$SourceDir = Join-Path $RepoRoot "assets\source\blender\W04\$AssetId"
$BlendFile = Join-Path $SourceDir ($AssetId + ".blend")
$ExchangeDir = Join-Path $RepoRoot "artifacts\local\blender\$AssetId"
$Manifest = Join-Path $ExchangeDir ($AssetId + "_blender_manifest.json")

foreach ($path in @($Factory,$Bridge,$Registry)) {
    if (-not (Test-Path $path)) { throw "Required path missing: $path" }
}

$registryData = Get-Content $Registry -Raw | ConvertFrom-Json
$matches = @($registryData.assets | Where-Object { $_.id -eq $AssetId })
if ($matches.Count -ne 1) {
    throw "Environment factory Asset ID must appear exactly once in registry: $AssetId"
}

New-Item -ItemType Directory -Force -Path $SourceDir | Out-Null

Write-Host "[NARIS ENV] Building canonical Ashen Forest Factory v2 .blend"
& $BlenderExe --background --factory-startup --python $Factory -- --out-blend $BlendFile
if ($LASTEXITCODE -ne 0) { throw "Ashen Forest Blender factory failed with exit code $LASTEXITCODE" }
if (-not (Test-Path $BlendFile)) { throw "Expected environment factory blend file was not produced: $BlendFile" }

Write-Host "[NARIS ENV] Running registry-gated Blender -> Unreal exchange"
& $Bridge -RepoRoot $RepoRoot -BlendFile $BlendFile -AssetId $AssetId -BlenderExe $BlenderExe -UnrealEngineRoot $UnrealEngineRoot
if ($LASTEXITCODE -ne 0) { throw "Ashen Forest Blender -> Unreal bridge failed with exit code $LASTEXITCODE" }
if (-not (Test-Path $Manifest)) { throw "Expected Blender exchange manifest was not produced: $Manifest" }

$manifestData = Get-Content $Manifest -Raw | ConvertFrom-Json
if ($manifestData.status -ne "pass") { throw "Ashen Forest Blender exchange manifest did not pass" }
if ($manifestData.asset_id -ne $AssetId) { throw "Ashen Forest Blender exchange manifest Asset ID mismatch" }

Write-Host "[NARIS ENV] Ashen Forest Factory v2 exchange PASSED"
Write-Host "[NARIS ENV] Blend: $BlendFile"
Write-Host "[NARIS ENV] Manifest: $Manifest"
