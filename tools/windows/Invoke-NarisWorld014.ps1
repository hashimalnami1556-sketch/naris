[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$PackageRoot,
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [switch]$RunEditor
)
$ErrorActionPreference = 'Stop'
$package = (Resolve-Path -LiteralPath $PackageRoot).Path
$project = Join-Path $RepoRoot 'unreal\NARIS_W04\NARIS_W04.uproject'
$importer = Join-Path $package 'Tools\ue57_build_world.py'
$manifest = Join-Path $package 'manifest.json'
$verifier = Join-Path $RepoRoot 'tools\ci\verify_world014_package.py'
$report = Join-Path $package 'UE5_AUTHORING_REPORT.json'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'

foreach ($file in @($project,$importer,$manifest,$verifier)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "WORLD-014 preflight missing required file: $file"
    }
}
$python = Get-Command python -ErrorAction Stop
& $python.Source $verifier $package
if ($LASTEXITCODE -ne 0) {
    throw 'WORLD-014 package integrity/ground alignment failed. No Unreal changes attempted.'
}
Write-Host '[WORLD-014] Offline file integrity and landmark elevation checks passed.'
if (-not $RunEditor) { return }

if (Test-Path -LiteralPath $report -PathType Leaf) {
    throw "Old UE report found: $report. Preserve and review before another run."
}
if (-not (Test-Path -LiteralPath $editor -PathType Leaf)) {
    throw "Unreal 5.7 editor not installed: $editor"
}
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'An UnrealEditor session is already open; close manually before authoring.'
}
$env:NARIS_WORLD014_ROOT = $package
& $editor $project "-ExecutePythonScript=$importer" -log -nosplash
if ($LASTEXITCODE -ne 0) {
    throw "Unreal authoring failed: exit $LASTEXITCODE; no release approval."
}
if (-not (Test-Path -LiteralPath $report -PathType Leaf)) {
    throw 'No editor authoring evidence produced.'
}
$data = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
if ($data.level_path -ne '/Game/NARIS/W04/Maps/W04_AshenForest_Work014') {
    throw 'Unrecognized work-level output; do not change GameDefaultMap.'
}
if ($data.terrain_actors -ne 64 -or $data.original_environment_landmarks -ne 2) {
    throw 'World actors incomplete; do not approve.'
}
Write-Host '[WORLD-014] Review level authored. PIE, BuildCookRun, visuals, network and FPS remain REQUIRED.'
