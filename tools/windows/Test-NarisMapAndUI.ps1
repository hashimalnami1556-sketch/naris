[CmdletBinding()]
param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$LocalProjectRoot = 'C:\Users\Admin\NARIS',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [switch]$RunUnrealMapValidation
)
$ErrorActionPreference = 'Stop'
$repoProject = Join-Path $RepoRoot 'unreal\NARIS_W04'
$uproject = Join-Path $repoProject 'NARIS_W04.uproject'
$iniPath = Join-Path $repoProject 'Config\DefaultEngine.ini'
$requiredMap = Join-Path $repoProject 'Content\NARIS\W04\Maps\W04_AshenForest.umap'
$prototypeMap = Join-Path $repoProject 'Content\NARIS\W04\Maps\W04_Prototype.umap'
$validator = Join-Path $repoProject 'Content\Python\naris_validate_shipping_map.py'
$editorCmd = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$reportDir = Join-Path $RepoRoot 'artifacts\diagnostics'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$reportFile = Join-Path $reportDir "naris_map_ui_$stamp.json"

$mapConfig = @{}
if (Test-Path -LiteralPath $iniPath) {
    $ini = Get-Content -LiteralPath $iniPath -Raw
    foreach ($key in @('EditorStartupMap','GameDefaultMap')) {
        $m = [regex]::Match($ini, "(?m)^$key=(.+)$")
        $mapConfig[$key] = if ($m.Success) { $m.Groups[1].Value.Trim() } else { $null }
    }
}
$localProject = Join-Path $LocalProjectRoot 'NARIS.uproject'
$localContent = Join-Path $LocalProjectRoot 'Content'
$localMaps = @()
if (Test-Path -LiteralPath $localContent -PathType Container) {
    $localMaps = @(Get-ChildItem -LiteralPath $localContent -Filter '*.umap' -Recurse -File -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty FullName)
}
$repoMaps = @()
if (Test-Path -LiteralPath (Join-Path $repoProject 'Content') -PathType Container) {
    $repoMaps = @(Get-ChildItem -LiteralPath (Join-Path $repoProject 'Content') -Filter '*.umap' -Recurse -File -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty FullName)
}
$report = [ordered]@{
    schema='naris.map-ui.diagnostics.v1'
    generated_at_utc=[DateTime]::UtcNow.ToString('o')
    repository_project_exists=(Test-Path -LiteralPath $uproject -PathType Leaf)
    local_project_exists=(Test-Path -LiteralPath $localProject -PathType Leaf)
    local_content_exists=(Test-Path -LiteralPath $localContent -PathType Container)
    engine_editor_exists=(Test-Path -LiteralPath $editorCmd -PathType Leaf)
    map_settings=$mapConfig
    production_map_exists=(Test-Path -LiteralPath $requiredMap -PathType Leaf)
    prototype_map_exists=(Test-Path -LiteralPath $prototypeMap -PathType Leaf)
    repo_map_files=$repoMaps
    local_map_files=$localMaps
    production_map_validator_exists=(Test-Path -LiteralPath $validator -PathType Leaf)
    map_validation='not_run'
    notes=@('Read-only diagnosis. No map or UI files were overwritten.',
            'The browser UI prototype is not an Unreal UMG widget.',
            'Map validation requires Unreal Engine 5.7 and an authored .umap.')
}
if ($RunUnrealMapValidation) {
    if (-not (Test-Path -LiteralPath $editorCmd -PathType Leaf)) { throw "UnrealEditor-Cmd.exe missing: $editorCmd" }
    if (-not (Test-Path -LiteralPath $uproject -PathType Leaf)) { throw "Unreal project missing: $uproject" }
    if (-not (Test-Path -LiteralPath $validator -PathType Leaf)) { throw "Validator missing: $validator" }
    if (-not $report.production_map_exists) {
        $report.map_validation = 'blocked_missing_production_map'
    } else {
        & $editorCmd $uproject "-ExecutePythonScript=$validator" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
        $exit = $LASTEXITCODE
        $report.map_validation = if ($exit -eq 0) {'pass'} else {"failed_exit_$exit"}
    }
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportFile -Encoding UTF8
Write-Host "[NARIS] Report: $reportFile"
Write-Host "[NARIS] Repo maps: $($repoMaps.Count) | Local maps: $($localMaps.Count)"
Write-Host "[NARIS] Production map exists: $($report.production_map_exists)"
Write-Host "[NARIS] GameDefaultMap: $($mapConfig.GameDefaultMap)"
Write-Host "[NARIS] No files changed."
if ($RunUnrealMapValidation -and $report.map_validation -ne 'pass') {
    throw "Production map validation did not pass: $($report.map_validation). Report: $reportFile"
}
