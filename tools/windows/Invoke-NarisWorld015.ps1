[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$PackageRoot,
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [switch]$RunEditor
)
$ErrorActionPreference = 'Stop'
$package = (Resolve-Path -LiteralPath $PackageRoot).Path
$uproject = Join-Path $RepoRoot 'unreal\NARIS_W04\NARIS_W04.uproject'
$verifier = Join-Path $package 'Tools\verify_world015_package.py'
$authoring = Join-Path $package 'Tools\ue57_build_world.py'
$report = Join-Path $package 'UE5_AUTHORING_REPORT.json'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
foreach ($p in @($uproject,$verifier,$authoring)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
        throw "WORLD-015 preflight missing required file: $p"
    }
}
$python = Get-Command python -ErrorAction Stop
& $python.Source $verifier $package
if ($LASTEXITCODE -ne 0) {
    throw 'WORLD-015 offline R16, actual GLB BIN, signed vertical bounds, approved PNG and SVG source validation FAILED. Do not start editor.'
}
Write-Host '[WORLD-015] 64 actual tiles / 5 source GLBs / 3 originals PNGs / 6 source SVGs preflight PASSED.'
if (-not $RunEditor) {
    Write-Host '[WORLD-015] Editor not invoked. Add -RunEditor ONLY on the machine with Unreal Engine 5.7.'
    return
}
if (Test-Path -LiteralPath $report -PathType Leaf) {
    throw "Existing authoring report blocks rerun: $report"
}
if (-not (Test-Path -LiteralPath $editor -PathType Leaf)) {
    throw "UnrealEditor-Cmd.exe not found: $editor"
}
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'An UnrealEditor session is open; stop manually before authoring.'
}
$env:NARIS_WORLD015_ROOT = $package
& $editor $uproject "-ExecutePythonScript=$authoring" -log -nosplash
if ($LASTEXITCODE -ne 0) {
    throw "UE authoring FAILED (exit $LASTEXITCODE). No shipping approval."
}
if (-not (Test-Path -LiteralPath $report -PathType Leaf)) {
    throw 'No editor-authored map report. Check engine logs, do not change default map.'
}
$data = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
if ($data.level_path -ne '/Game/NARIS/W04/Maps/W04_AshenForest_Work015') {
    throw 'Unexpected editor output map.'
}
if ($data.terrain_actors -ne 64 -or $data.original_environment_landmarks -ne 2) {
    throw 'Editor map missing expected original terrain or environment actors.'
}
if ($data.ui_reference_textures_imported -ne 3 -or $data.new_hud_icon_textures_imported -ne 6) {
    throw 'Not all original UI references or six authored icons imported.'
}
Write-Host '[WORLD-015] Isolated review map saved. PIE, before/after/diff, 2-client net, BuildCookRun and FPS still NOT RUN.'
