[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [string]$ReportOut = '',
    [switch]$RunEditor
)
$ErrorActionPreference = 'Stop'
$uproject = Join-Path $RepoRoot 'unreal\NARIS_W04\NARIS_W04.uproject'
$auditor = Join-Path $RepoRoot 'tools\ui\verify_ui017_hud_assets.py'
$hudSource = Join-Path $RepoRoot 'unreal\NARIS_W04\Source\NARIS_W04\Private\NarisHUD.cpp'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
foreach ($p in @($uproject, $auditor, $hudSource)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
        throw "UI-017 missing required source: $p"
    }
}
# Offline source prerequisite. Does not substitute Unreal compilation.
$cpp = Get-Content -LiteralPath $hudSource -Raw
foreach ($key in @('health','mana','energy','attack','defense','map')) {
    $expected = 'DrawGameIcon(TEXT("' + $key + '")'
    if (-not $cpp.Contains($expected)) {
        throw "UI-017 gameplay icon not bound in native HUD: $key"
    }
}
Write-Host '[UI-017] Offline gameplay HUD references: 6/6 source icon names present.'
if (-not $RunEditor) {
    Write-Host '[UI-017] Unreal not started. Pass -RunEditor ONLY on the authorized UE5.7 workstation.'
    return
}
if (-not (Test-Path -LiteralPath $editor -PathType Leaf)) {
    throw "UnrealEditor-Cmd.exe unavailable: $editor"
}
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'UnrealEditor is already open. Exit it before command-line asset QA.'
}
if ([string]::IsNullOrWhiteSpace($ReportOut)) {
    $ReportOut = Join-Path $RepoRoot 'docs\changes\UI-017\UI017_EDITOR_AUDIT_LOCAL.json'
}
$report = [System.IO.Path]::GetFullPath($ReportOut)
if (Test-Path -LiteralPath $report -PathType Leaf) {
    throw "Existing editor evidence may not be overwritten: $report"
}
$env:NARIS_UI017_AUDIT_REPORT = $report
& $editor $uproject "-ExecutePythonScript=$auditor" -log -nosplash
if ($LASTEXITCODE -ne 0) {
    throw "Actual UE5.7 editor texture audit FAILED with exit code $LASTEXITCODE."
}
if (-not (Test-Path -LiteralPath $report -PathType Leaf)) {
    throw 'Editor reported success but did not write UI017 audit receipt.'
}
$data = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
if ($data.status -ne 'IMPORT_ASSETS_PRESENT' -or @($data.icons).Count -ne 6) {
    throw 'Missing or invalid original six Texture2D icons. Build/release blocked.'
}
Write-Host '[UI-017] Six real imported Texture2D assets PASS; PIE screenshots, RTL, network and full BuildCookRun still required.'
