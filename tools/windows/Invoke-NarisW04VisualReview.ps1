# NARIS W04 visual preview launcher - deliberately separate from runtime smoke.
[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT,
    [ValidateSet("Blockout", "Production")][string]$Map = "Blockout",
    [switch]$PrepareBlockout,
    [switch]$InspectOnly
)
$ErrorActionPreference = "Stop"
if (-not $UnrealEngineRoot) {
    $UnrealEngineRoot = "C:\Program Files\Epic Games\UE_5.7"
}
$uproject = Join-Path $RepoRoot "unreal/NARIS_W04/NARIS_W04.uproject"
$editor = Join-Path $UnrealEngineRoot "Engine/Binaries/Win64/UnrealEditor.exe"
$mapDir = Join-Path $RepoRoot "unreal/NARIS_W04/Content/NARIS/W04/Maps"
$mapName = if ($Map -eq "Production") { "W04_AshenForest" } else { "W04_AshenForest_Blockout" }
$mapFile = Join-Path $mapDir ($mapName + ".umap")
$mapPath = "/Game/NARIS/W04/Maps/" + $mapName
$engineConfig = Join-Path $RepoRoot "unreal/NARIS_W04/Config/DefaultEngine.ini"
foreach ($required in @($uproject, $editor, $engineConfig)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "NARIS_VISUAL_PREVIEW_BLOCKED: missing required file $required"
    }
}
if ($PrepareBlockout) {
    if ($Map -ne "Blockout") {
        throw "PrepareBlockout is only supported for the non-shipping Blockout map."
    }
    $author = Join-Path $RepoRoot "tools/windows/Invoke-NarisW04ProductionBlockout.ps1"
    if (-not (Test-Path -LiteralPath $author)) { throw "Missing authoring tool: $author" }
    & $author -RepoRoot $RepoRoot -UnrealEngineRoot $UnrealEngineRoot
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "Blockout authoring failed ($LASTEXITCODE)."
    }
}
if (-not (Test-Path -LiteralPath $mapFile)) {
    throw (("NARIS_VISUAL_PREVIEW_BLOCKED: {0} is missing. " +
        "Do not substitute W04_Prototype. Build the blockout with -PrepareBlockout " +
        "or author and validate the production map in Unreal.") -f $mapFile)
}
if ((Get-Item -LiteralPath $mapFile).Length -eq 0) {
    throw "NARIS_VISUAL_PREVIEW_BLOCKED: map is empty: $mapFile"
}
$ini = Get-Content -Raw -LiteralPath $engineConfig
if ($ini -match "GameDefaultMap=/Game/NARIS/W04/Maps/W04_Prototype") {
    Write-Warning "DefaultGameMap still targets W04_Prototype (SMOKE ONLY). This launcher selects $mapName explicitly."
}
if ($Map -eq "Production") {
    Write-Warning "Production map file existence is NOT shipping approval. Complete full release map, assets, gameplay, performance, and QA gates."
}
Write-Host "NARIS_VISUAL_PREVIEW_TARGET=$mapPath"
Write-Host "NARIS_VISUAL_PREVIEW_MAP_BYTES=$((Get-Item -LiteralPath $mapFile).Length)"
if ($InspectOnly) { Write-Host "NARIS_VISUAL_PREVIEW_INSPECT_PASS"; return }
$args = @(
    ('"' + $uproject + '"'),
    $mapPath,
    "-game", "-log", "-windowed", "-ResX=1600", "-ResY=900"
)
$process = Start-Process -FilePath $editor -ArgumentList $args -PassThru
Write-Host "NARIS_VISUAL_PREVIEW_STARTED_PID=$($process.Id)"
Write-Host "Preview is a review session, not a validated Shipping build."
