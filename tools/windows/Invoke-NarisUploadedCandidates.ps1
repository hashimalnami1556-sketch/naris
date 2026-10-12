param(
    [string]$RepoRoot = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent),
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT,
    [switch]$SkipBuild,
    [switch]$NoLaunch
)
$ErrorActionPreference = 'Stop'
if (-not $UnrealEngineRoot) { $UnrealEngineRoot = 'C:\Program Files\Epic Games\UE_5.7' }
$RepoRoot = (Resolve-Path $RepoRoot).Path
$project = Join-Path $RepoRoot 'unreal\NARIS_W04\NARIS_W04.uproject'
$script = Join-Path $RepoRoot 'unreal\NARIS_W04\Content\Python\naris_import_uploaded_candidates.py'
$build = Join-Path $UnrealEngineRoot 'Engine\Build\BatchFiles\Build.bat'
$commandlet = Join-Path $UnrealEngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$editor = Join-Path $UnrealEngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
foreach ($path in @($project,$script,$build,$commandlet,$editor)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing required path: $path" }
}
$running = Get-Process -Name UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue
if ($running) { throw 'Close Unreal Editor before building/importing. Existing processes will not be terminated.' }
if (-not $SkipBuild) {
    & $build NARIS_W04Editor Win64 Development "-Project=$project" -WaitMutex -NoHotReloadFromIDE
    if ($LASTEXITCODE -ne 0) { throw "Editor build failed: $LASTEXITCODE" }
}
& $commandlet $project "-ExecutePythonScript=$script" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) { throw "Candidate import failed: $LASTEXITCODE. Inspect Saved\Logs." }
$mapFile = Join-Path $RepoRoot 'unreal\NARIS_W04\Content\NARIS\Intake\W04_20261011\Maps\DEV_IntakeReview.umap'
if (-not (Test-Path -LiteralPath $mapFile)) { throw 'Import did not create the review map.' }
if (-not $NoLaunch) {
    # Editor review only. This does not package a release or change startup maps.
    Start-Process -FilePath $editor -ArgumentList @(('"{0}"' -f $project),'/Game/NARIS/Intake/W04_20261011/Maps/DEV_IntakeReview','-NarisSkipFrontEnd')
}
Write-Host 'Candidate review map available. Use Play to inspect; gameplay art remains unchanged.'
