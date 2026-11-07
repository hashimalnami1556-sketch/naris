[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackageRoot,
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [switch]$RunEditor
)
$ErrorActionPreference = 'Stop'
$uproject = Join-Path $RepoRoot 'unreal\NARIS_W04\NARIS_W04.uproject'
$source = Join-Path $PackageRoot 'Tools\ue57_build_world.py'
$manifest = Join-Path $PackageRoot 'manifest.json'
$verify = Join-Path $RepoRoot 'tools\ci\verify_world013_package.py'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'

foreach ($p in @($uproject, $source, $manifest, $verify)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
        throw "WORLD-013 preflight missing required file: $p"
    }
}
$python = Get-Command python -ErrorAction Stop
& $python.Source $verify $PackageRoot
if ($LASTEXITCODE -ne 0) { throw 'WORLD-013 offline integrity gate failed. No editor launched.' }
if (-not $RunEditor) {
    Write-Host 'WORLD-013 offline integrity PASS. Use -RunEditor to stage a review map, not to release.'
    return
}
if (-not (Test-Path -LiteralPath $editor -PathType Leaf)) {
    throw "UE5.7 Editor not installed: $editor"
}
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'UnrealEditor already running; do not patch a live session.'
}

# This environment variable is read by the package's guarded authoring script.
$env:NARIS_WORLD013_ROOT = (Resolve-Path -LiteralPath $PackageRoot).Path
& $editor $uproject "-ExecutePythonScript=$source" -log -nosplash
if ($LASTEXITCODE -ne 0) { throw "UE editor failed (exit $LASTEXITCODE); no approved release" }
$report = Join-Path $PackageRoot 'UE5_AUTHORING_REPORT.json'
if (-not (Test-Path -LiteralPath $report -PathType Leaf)) {
    throw "No Unreal map authoring evidence: $report"
}
$payload = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
if ($payload.level_path -ne '/Game/NARIS/W04/Maps/W04_AshenForest_Work013') {
    throw 'Unexpected level output path. No release approval.'
}
Write-Host 'Review level generated. PIE screenshots, collision, gameplay, network and FPS still REQUIRED.'
