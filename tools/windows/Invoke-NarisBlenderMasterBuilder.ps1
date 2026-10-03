param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
  [string]$BlenderExe = $env:BLENDER_EXE,
  [switch]$ExportCoreAssets
)
$ErrorActionPreference = "Stop"
if (-not $BlenderExe) {
  $candidates = @(
    "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
  )
  $BlenderExe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) { throw "blender.exe not found. Set BLENDER_EXE." }

$Builder = Join-Path $RepoRoot "tools\blender\NARIS_Blender_Master_Builder_v1_1.py"
$Exporter = Join-Path $RepoRoot "tools\blender\naris_export.py"
$Registry = Join-Path $RepoRoot "data\MASTER_ASSET_REGISTRY.json"
$ArtifactRoot = Join-Path $RepoRoot "artifacts\local\blender\master-builder-v1_1"
$BlendFile = Join-Path $ArtifactRoot "NARIS_Master_W04.blend"
$ValidationDir = Join-Path $ArtifactRoot "validation"
$ManifestDir = Join-Path $ArtifactRoot "manifest"
New-Item -ItemType Directory -Force -Path $ArtifactRoot,$ValidationDir,$ManifestDir | Out-Null

$env:NARIS_REPO_ROOT = $RepoRoot
Write-Host "Building NARIS W04 authoring scene with Blender..."
& $BlenderExe --background --python $Builder
if ($LASTEXITCODE -ne 0) { throw "Blender Master Builder failed with exit code $LASTEXITCODE" }

# The builder may save to its configured output; retain a deterministic invocation record.
@{
  timestamp=(Get-Date).ToString("o")
  blender=$BlenderExe
  builder=$Builder
  registry=$Registry
  status="builder_completed"
} | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $ValidationDir "builder-run.json")

$coreAssets = @(
  "NARIS-W04-CHR-HERO-0001",
  "NARIS-W04-CHR-COMPANION-0001",
  "NARIS-W04-ENM-BONEBEAST-0001",
  "NARIS-W04-PRP-WAYSTONE-0001",
  "NARIS-W04-PRP-MEMORYCRYSTAL-0001",
  "NARIS-W04-PRP-ASHGATE-0001",
  "NARIS-W04-WPN-SWORD-0001"
)
$coreAssets | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $ManifestDir "core-assets.json")

if ($ExportCoreAssets) {
  if (-not (Test-Path $BlendFile)) {
    Write-Warning "NARIS_Master_W04.blend was not found at deterministic artifact path; registry-gated per-asset export is deferred."
  } else {
    foreach ($AssetId in $coreAssets) {
      $Out = Join-Path $ArtifactRoot $AssetId
      New-Item -ItemType Directory -Force -Path $Out | Out-Null
      & $BlenderExe --background $BlendFile --python $Exporter -- --out $Out --asset-id $AssetId --registry $Registry
      if ($LASTEXITCODE -ne 0) { throw "Registry-gated export failed for $AssetId" }
    }
  }
}
Write-Host "NARIS Blender Master Builder pipeline completed. Evidence: $ArtifactRoot"
