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
$AnimationReport = Join-Path $RepoRoot "unreal\NARIS_W04\Saved\TestReports\naris_animation_validation.json"
$ProductionAssetReport = Join-Path $RepoRoot "unreal\NARIS_W04\Saved\TestReports\naris_production_asset_validation.json"
$PresentationAudioReport = Join-Path $RepoRoot "unreal\NARIS_W04\Saved\TestReports\naris_presentation_audio_import.json"
$PresentationBindingReport = Join-Path $RepoRoot "unreal\NARIS_W04\Saved\TestReports\naris_presentation_binding_resolution.json"
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

if (-not (Test-Path $AnimationReport)) {
    throw "Animation validation report was not produced: $AnimationReport"
}
if (-not (Test-Path $ProductionAssetReport)) {
    throw "Production asset validation report was not produced: $ProductionAssetReport"
}
if (-not (Test-Path $PresentationAudioReport)) {
    throw "Presentation audio import report was not produced: $PresentationAudioReport"
}
if (-not (Test-Path $PresentationBindingReport)) {
    throw "Presentation binding resolution report was not produced: $PresentationBindingReport"
}
if (-not (Test-Path $PresentationAuthoringReport)) {
    throw "Presentation authoring report was not produced: $PresentationAuthoringReport"
}

$AnimationData = Get-Content $AnimationReport -Raw | ConvertFrom-Json
if ($AnimationData.status -ne "pass") {
    throw "Animation validation failed: $AnimationReport"
}

$ProductionAssetData = Get-Content $ProductionAssetReport -Raw | ConvertFrom-Json
if ($ProductionAssetData.status -ne "pass") {
    throw "Production asset validation failed: $ProductionAssetReport"
}

$PresentationAudioData = Get-Content $PresentationAudioReport -Raw | ConvertFrom-Json
if ($PresentationAudioData.status -ne "pass") {
    throw "Presentation audio import failed: $PresentationAudioReport"
}

$PresentationBindingData = Get-Content $PresentationBindingReport -Raw | ConvertFrom-Json
if ($PresentationBindingData.status -ne "pass") {
    throw "Presentation binding resolution failed: $PresentationBindingReport"
}

$PresentationAuthoringData = Get-Content $PresentationAuthoringReport -Raw | ConvertFrom-Json
if ($PresentationAuthoringData.status -ne "pass") {
    throw "Presentation authoring failed: $PresentationAuthoringReport"
}

Copy-Item $AnimationReport (Join-Path $ArchiveDir "naris_animation_validation.json") -Force
Copy-Item $ProductionAssetReport (Join-Path $ArchiveDir "naris_production_asset_validation.json") -Force
Copy-Item $PresentationAudioReport (Join-Path $ArchiveDir "naris_presentation_audio_import.json") -Force
Copy-Item $PresentationBindingReport (Join-Path $ArchiveDir "naris_presentation_binding_resolution.json") -Force
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

$SmokeStartedAtUtc = [DateTime]::UtcNow
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

$RuntimeEvidenceRoots = @(
    $ArchiveDir,
    (Join-Path $env:LOCALAPPDATA "NARIS_W04\Saved")
)

$RuntimeLogFiles = @()
$CrashArtifacts = @()
foreach ($root in $RuntimeEvidenceRoots) {
    if (-not (Test-Path $root)) {
        continue
    }

    $RuntimeLogFiles += @(
        Get-ChildItem -Path $root -Filter "*.log" -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTimeUtc -ge $SmokeStartedAtUtc } |
        Select-Object -ExpandProperty FullName
    )

    $CrashRoot = Join-Path $root "Crashes"
    if (Test-Path $CrashRoot) {
        $CrashArtifacts += @(
            Get-ChildItem -Path $CrashRoot -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTimeUtc -ge $SmokeStartedAtUtc } |
            Select-Object -ExpandProperty FullName
        )
    }
}

$FatalPatterns = @(
    "Fatal error:",
    "Unhandled Exception",
    "Assertion failed:",
    "LowLevelFatalError",
    "Ensure condition failed:"
)

$FatalFindings = @()
foreach ($logPath in @($RuntimeLogFiles | Select-Object -Unique)) {
    foreach ($pattern in $FatalPatterns) {
        $matches = Select-String -Path $logPath -Pattern $pattern -SimpleMatch -ErrorAction SilentlyContinue
        foreach ($match in $matches) {
            $FatalFindings += [ordered]@{
                file = $logPath
                line = $match.LineNumber
                pattern = $pattern
                text = $match.Line.Trim()
            }
        }
    }
}

$RuntimeLogQaStatus = if (
    $FatalFindings.Count -eq 0 -and $CrashArtifacts.Count -eq 0
) { "pass" } else { "fail" }

$RuntimeLogQaReport = [ordered]@{
    schema = "naris.windows.runtime-log-qa.v1"
    status = $RuntimeLogQaStatus
    smoke_started_at_utc = $SmokeStartedAtUtc.ToString("o")
    log_files = @($RuntimeLogFiles | Select-Object -Unique)
    crash_artifacts = @($CrashArtifacts | Select-Object -Unique)
    fatal_findings = @($FatalFindings)
}

$RuntimeLogQaReportPath = Join-Path $ArchiveDir "naris_runtime_log_qa.json"
$RuntimeLogQaReport |
    ConvertTo-Json -Depth 7 |
    Set-Content -Path $RuntimeLogQaReportPath -Encoding UTF8

if ($RuntimeLogQaStatus -ne "pass") {
    throw "Runtime log/crash QA failed. See $RuntimeLogQaReportPath"
}

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
    animation_validation_status = $AnimationData.status
    production_asset_validation_status = $ProductionAssetData.status
    production_asset_validated_asset_ids = @($ProductionAssetData.validated_asset_ids)
    production_asset_unresolved_asset_ids = @($ProductionAssetData.unresolved_asset_ids)
    animation_validated_asset_ids = @($AnimationData.validated_asset_ids)
    animation_unresolved_asset_ids = @($AnimationData.unresolved_asset_ids)
    presentation_audio_import_status = $PresentationAudioData.status
    presentation_audio_imported_asset_ids = @($PresentationAudioData.imported_asset_ids)
    presentation_audio_missing_asset_ids = @($PresentationAudioData.skipped_missing_asset_ids)
    presentation_binding_resolution_status = $PresentationBindingData.status
    presentation_resolved_asset_ids = @($PresentationBindingData.resolved_asset_ids)
    presentation_already_bound_asset_ids = @($PresentationBindingData.already_bound_asset_ids)
    presentation_unresolved_asset_ids = @($PresentationBindingData.unresolved_asset_ids)
    presentation_authoring_status = $PresentationAuthoringData.status
    presentation_bound_asset_ids = @($PresentationAuthoringData.bound_asset_ids)
    presentation_unbound_asset_ids = @($PresentationAuthoringData.unbound_asset_ids)
    presentation_unbound_expected_paths = $PresentationAuthoringData.unbound_expected_paths
    csv_capture_files = @($CsvCaptures)
    llm_capture_files = @($LlmCaptures)
    runtime_log_qa_status = $RuntimeLogQaStatus
    runtime_log_qa_report = $RuntimeLogQaReportPath
    runtime_log_files = @($RuntimeLogFiles | Select-Object -Unique)
    crash_artifacts = @($CrashArtifacts | Select-Object -Unique)
    profiling_note = "CSV/LLM capture paths are evidence only when files are emitted by the packaged Development build."
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
}

$ReportPath = Join-Path $ArchiveDir "naris_windows_package_smoke.json"
$Report | ConvertTo-Json -Depth 5 | Set-Content -Path $ReportPath -Encoding UTF8

Write-Host "[NARIS] Windows package + launch smoke PASSED"
Write-Host "[NARIS] Report: $ReportPath"
