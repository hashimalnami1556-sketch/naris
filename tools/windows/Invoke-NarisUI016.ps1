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
$importer = Join-Path $RepoRoot 'tools\ui\import_naris_ui016_icons.py'
$report = Join-Path $package 'UI016_IMPORT_REPORT.json'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
foreach ($path in @($uproject,$importer, (Join-Path $package 'manifest.json'))) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "UI-016 missing source: $path"
    }
}
$python = Get-Command python -ErrorAction Stop
$env:NARIS_UI016_ICON_ROOT = $package
& $python.Source $importer --check
if ($LASTEXITCODE -ne 0) {
    throw 'UI-016 original UI/SVG/PNG source integrity failed. Unreal was not started.'
}
Write-Host '[UI-016] Exact three approved UI screens and six original PNG+SVG source hashes verified.'
if (-not $RunEditor) {
    Write-Host '[UI-016] Offline preflight only; -RunEditor imports Texture2D when UE5.7 is installed.'
    return
}
if (Test-Path -LiteralPath $report -PathType Leaf) {
    throw "Existing UI-016 import report; protect prior import before rerunning: $report"
}
if (-not (Test-Path -LiteralPath $editor -PathType Leaf)) {
    throw "UE5.7 commandlet executable missing: $editor"
}
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'Editor already running; close it to avoid concurrent content changes.'
}
& $editor $uproject "-ExecutePythonScript=$importer" -log -nosplash
if ($LASTEXITCODE -ne 0) {
    throw "Unreal UI texture import failed. Exit $LASTEXITCODE"
}
if (-not (Test-Path -LiteralPath $report -PathType Leaf)) {
    throw 'No asset import receipt; release blocked.'
}
$data = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
if ($data.status -ne 'TEXTURE2D_IMPORT_ONLY' -or @($data.icon_assets).Count -ne 6) {
    throw 'Missing native UMG Texture2D icon evidence; release blocked.'
}
Write-Host '[UI-016] Six stable Texture2D paths imported. Restart PIE and verify real visuals, Arabic RTL, gameplay and cook.'
