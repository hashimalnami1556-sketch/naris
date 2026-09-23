param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT,
    [string]$ArchiveDir = ""
)

$ErrorActionPreference = "Stop"

if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

if (-not $ArchiveDir) {
    $ArchiveDir = Join-Path $RepoRoot "artifacts\windows\NARIS_W04_RC"
}

$UProject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$BuildBat = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\Build.bat"
$RunUAT = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\RunUAT.bat"
$Bootstrap = Join-Path $RepoRoot "tools\windows\Invoke-NarisW04AuthoringBootstrap.ps1"
$Localization = Join-Path $RepoRoot "tools\windows\Invoke-NarisLocalization.ps1"
$PresentationReport = Join-Path $RepoRoot "unreal\NARIS_W04\Saved\TestReports\naris_presentation_authoring.json"

foreach ($path in @($UProject, $BuildBat, $RunUAT, $Bootstrap, $Localization)) {
    if (-not (Test-Path $path)) {
        throw "Required path missing: $path"
    }
}

New-Item -ItemType Directory -Force -Path $ArchiveDir | Out-Null

Write-Host "[NARIS RC] Building editor"
& $BuildBat "NARIS_W04Editor" "Win64" "Development" $UProject "-WaitMutex"
if ($LASTEXITCODE -ne 0) {
    throw "Editor build failed with exit code $LASTEXITCODE"
}

$env:NARIS_PRESENTATION_STRICT = "1"
try {
    Write-Host "[NARIS RC] Authoring W04 with strict presentation bindings"
    & $Bootstrap -RepoRoot $RepoRoot -UnrealEngineRoot $UnrealEngineRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Strict authoring bootstrap failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item Env:NARIS_PRESENTATION_STRICT -ErrorAction SilentlyContinue
}

if (-not (Test-Path $PresentationReport)) {
    throw "Strict presentation report missing: $PresentationReport"
}

$Presentation = Get-Content $PresentationReport -Raw | ConvertFrom-Json
if ($Presentation.status -ne "pass") {
    throw "Strict presentation authoring did not pass"
}
if (@($Presentation.unbound_asset_ids).Count -ne 0) {
    throw "Release candidate has unbound presentation assets"
}
if (@($Presentation.errors).Count -ne 0) {
    throw "Release candidate presentation authoring contains errors"
}

Write-Host "[NARIS RC] Compiling localization"
& $Localization -RepoRoot $RepoRoot -UnrealEngineRoot $UnrealEngineRoot
if ($LASTEXITCODE -ne 0) {
    throw "Localization failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS RC] Building Shipping package"
$UatArgs = @(
    "BuildCookRun",
    "-project=$UProject",
    "-noP4",
    "-platform=Win64",
    "-clientconfig=Shipping",
    "-build",
    "-cook",
    "-map=W04_Prototype",
    "-stage",
    "-pak",
    "-package",
    "-archive",
    "-archivedirectory=$ArchiveDir",
    "-utf8output"
)
& $RunUAT @UatArgs
if ($LASTEXITCODE -ne 0) {
    throw "Release candidate BuildCookRun failed with exit code $LASTEXITCODE"
}

$Executable = Get-ChildItem -Path $ArchiveDir -Filter "NARIS_W04.exe" -Recurse -File |
    Select-Object -First 1
if (-not $Executable) {
    throw "Release candidate executable not found"
}

$Report = [ordered]@{
    schema = "naris.windows.release-candidate.v1"
    status = "pass"
    platform = "Win64"
    configuration = "Shipping"
    executable = $Executable.FullName
    presentation_bound_count = @($Presentation.bound_asset_ids).Count
    presentation_unbound_count = @($Presentation.unbound_asset_ids).Count
    presentation_error_count = @($Presentation.errors).Count
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
}

$ReportPath = Join-Path $ArchiveDir "naris_release_candidate.json"
$Report | ConvertTo-Json -Depth 5 | Set-Content -Path $ReportPath -Encoding UTF8

Write-Host "[NARIS RC] Release candidate gate PASSED"
Write-Host "[NARIS RC] Report: $ReportPath"
