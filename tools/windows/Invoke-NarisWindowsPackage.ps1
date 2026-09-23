param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT,
    [string]$ArchiveDir = "",
    [int]$LaunchSmokeSeconds = 20
)

$ErrorActionPreference = "Stop"

if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

if (-not $ArchiveDir) {
    $ArchiveDir = Join-Path $RepoRoot "artifacts\windows\NARIS_W04"
}

$UProject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$BuildBat = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\Build.bat"
$RunUAT = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\RunUAT.bat"
$Bootstrap = Join-Path $RepoRoot "tools\windows\Invoke-NarisW04AuthoringBootstrap.ps1"
$Localization = Join-Path $RepoRoot "tools\windows\Invoke-NarisLocalization.ps1"
$GeneratedMap = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Maps\W04_Prototype.umap"
$GeneratedBossData = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Data\DA_BoneBeast_Smoke.uasset"
$GeneratedPresentationProfile = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Presentation\DA_W04_Presentation.uasset"
$PresentationAuthoringReport = Join-Path $RepoRoot "unreal\NARIS_W04\Saved\TestReports\naris_presentation_authoring.json"

foreach ($path in @($UProject, $BuildBat, $RunUAT, $Bootstrap, $Localization)) {
    if (-not (Test-Path $path)) {
        throw "Required path missing: $path"
    }
}

New-Item -ItemType Directory -Force -Path $ArchiveDir | Out-Null

Write-Host "[NARIS] Building NARIS_W04Editor"
& $BuildBat "NARIS_W04Editor" "Win64" "Development" $UProject "-WaitMutex"
if ($LASTEXITCODE -ne 0) {
    throw "NARIS_W04Editor build failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Generating W04 runtime-smoke map/assets"
& $Bootstrap -RepoRoot $RepoRoot -UnrealEngineRoot $UnrealEngineRoot
if ($LASTEXITCODE -ne 0) {
    throw "W04 authoring bootstrap failed with exit code $LASTEXITCODE"
}

foreach ($generated in @($GeneratedMap, $GeneratedBossData, $GeneratedPresentationProfile)) {
    if (-not (Test-Path $generated)) {
        throw "Expected generated Unreal asset is missing: $generated"
    }
}

if (-not (Test-Path $PresentationAuthoringReport)) {
    throw "Presentation authoring report was not produced: $PresentationAuthoringReport"
}

$PresentationAuthoringData = Get-Content $PresentationAuthoringReport -Raw | ConvertFrom-Json
if ($PresentationAuthoringData.status -ne "pass") {
    throw "Presentation authoring failed: $PresentationAuthoringReport"
}

Copy-Item $PresentationAuthoringReport (Join-Path $ArchiveDir "naris_presentation_authoring.json") -Force

Write-Host "[NARIS] Gathering and compiling EN/AR localization"
& $Localization -RepoRoot $RepoRoot -UnrealEngineRoot $UnrealEngineRoot
if ($LASTEXITCODE -ne 0) {
    throw "Localization pipeline failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] BuildCookRun Win64 Development"
$UatArgs = @(
    "BuildCookRun",
    "-project=$UProject",
    "-noP4",
    "-platform=Win64",
    "-clientconfig=Development",
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
    throw "BuildCookRun failed with exit code $LASTEXITCODE"
}

$Executable = Get-ChildItem -Path $ArchiveDir -Filter "NARIS_W04.exe" -Recurse -File |
    Select-Object -First 1

if (-not $Executable) {
    throw "Packaged NARIS_W04.exe was not found under $ArchiveDir"
}

$RuntimeSmokeReport = Join-Path $ArchiveDir "naris_runtime_smoke.json"
if (Test-Path $RuntimeSmokeReport) {
    Remove-Item $RuntimeSmokeReport -Force
}

Write-Host "[NARIS] Runtime progression + save/load smoke"
$RuntimeSmokeProcess = Start-Process -FilePath $Executable.FullName -ArgumentList @(
    "-nosplash",
    "-windowed",
    "-ResX=1280",
    "-ResY=720",
    "-log",
    "-culture=en",
    "-NarisRuntimeSmoke",
    "-NarisSmokeReport=`"$RuntimeSmokeReport`""
) -PassThru

if (-not $RuntimeSmokeProcess.WaitForExit(60000)) {
    Stop-Process -Id $RuntimeSmokeProcess.Id -Force -ErrorAction SilentlyContinue
    throw "Runtime progression smoke timed out after 60 seconds"
}

if (-not (Test-Path $RuntimeSmokeReport)) {
    throw "Runtime smoke report was not produced: $RuntimeSmokeReport"
}

$RuntimeSmokeData = Get-Content $RuntimeSmokeReport -Raw | ConvertFrom-Json
if ($RuntimeSmokeData.status -ne "pass") {
    throw "Runtime progression smoke failed: $($RuntimeSmokeData.detail)"
}

Write-Host "[NARIS] Runtime progression smoke PASSED"

Write-Host "[NARIS] Launch smoke: $($Executable.FullName)"
$Process = Start-Process -FilePath $Executable.FullName -ArgumentList @(
    "-nosplash",
    "-windowed",
    "-ResX=1280",
    "-ResY=720",
    "-log",
    "-culture=en",
    "-csvCaptureFrames=600",
    "-csvGpuStats",
    "-LLMCSV"
) -PassThru

Start-Sleep -Seconds $LaunchSmokeSeconds

if ($Process.HasExited) {
    throw "Packaged game exited during launch smoke with code $($Process.ExitCode)"
}

Stop-Process -Id $Process.Id -Force
Start-Sleep -Seconds 2

Write-Host "[NARIS] Arabic culture launch smoke"
$ArabicProcess = Start-Process -FilePath $Executable.FullName -ArgumentList @(
    "-nosplash",
    "-windowed",
    "-ResX=1280",
    "-ResY=720",
    "-log",
    "-culture=ar"
) -PassThru

Start-Sleep -Seconds ([Math]::Min($LaunchSmokeSeconds, 10))

if ($ArabicProcess.HasExited) {
    throw "Arabic packaged game exited during launch smoke with code $($ArabicProcess.ExitCode)"
}

Stop-Process -Id $ArabicProcess.Id -Force
Start-Sleep -Seconds 2

$ProfilingRoots = @(
    (Join-Path $ArchiveDir "Saved\Profiling"),
    (Join-Path $env:LOCALAPPDATA "NARIS_W04\Saved\Profiling")
)

$CsvCaptures = @()
$LlmCaptures = @()
foreach ($root in $ProfilingRoots) {
    if (Test-Path $root) {
        $CsvCaptures += @(
            Get-ChildItem -Path $root -Filter "*.csv" -Recurse -File |
            Where-Object { $_.FullName -match "[\\/]CSV[\\/]" } |
            Select-Object -ExpandProperty FullName
        )
        $LlmCaptures += @(
            Get-ChildItem -Path $root -Filter "*.csv" -Recurse -File |
            Where-Object { $_.FullName -match "[\\/]LLM[\\/]" } |
            Select-Object -ExpandProperty FullName
        )
    }
}

$Report = [ordered]@{
    schema = "naris.windows.package-smoke.v1"
    status = "pass"
    configuration = "Development"
    platform = "Win64"
    archive = $ArchiveDir
    executable = $Executable.FullName
    launch_smoke_seconds = $LaunchSmokeSeconds
    localization_launch_smoke = @("en", "ar")
    runtime_progression_smoke = $RuntimeSmokeData.status
    runtime_progression_report = $RuntimeSmokeReport
    generated_map = $GeneratedMap
    generated_boss_data = $GeneratedBossData
    generated_presentation_profile = $GeneratedPresentationProfile
    presentation_authoring_status = $PresentationAuthoringData.status
    presentation_bound_asset_ids = @($PresentationAuthoringData.bound_asset_ids)
    presentation_unbound_asset_ids = @($PresentationAuthoringData.unbound_asset_ids)
    csv_capture_files = @($CsvCaptures)
    llm_capture_files = @($LlmCaptures)
    profiling_note = "CSV/LLM capture paths are evidence only when files are emitted by the packaged Development build."
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
}

$ReportPath = Join-Path $ArchiveDir "naris_windows_package_smoke.json"
$Report | ConvertTo-Json -Depth 5 | Set-Content -Path $ReportPath -Encoding UTF8

Write-Host "[NARIS] Windows package + launch smoke PASSED"
Write-Host "[NARIS] Report: $ReportPath"
