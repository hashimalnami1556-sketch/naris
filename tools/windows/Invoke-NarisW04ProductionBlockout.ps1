param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT
)

$ErrorActionPreference = "Stop"

if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

$UProject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$BuildBat = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\Build.bat"
$UnrealCmd = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$Script = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_author_w04_production_blockout.py"

foreach ($path in @($UProject,$BuildBat,$UnrealCmd,$Script)) {
    if (-not (Test-Path $path)) {
        throw "Required path missing: $path"
    }
}

Write-Host "[NARIS] Building editor before Ashen Forest production blockout authoring"
& $BuildBat "NARIS_W04Editor" "Win64" "Development" $UProject "-WaitMutex"
if ($LASTEXITCODE -ne 0) {
    throw "NARIS_W04Editor build failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] Authoring W04_AshenForest_Blockout from canonical LEVEL_LAYOUT"
& $UnrealCmd $UProject "-ExecutePythonScript=$Script" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "Ashen Forest production blockout authoring failed with exit code $LASTEXITCODE"
}

$Blockout = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Maps\W04_AshenForest_Blockout.umap"
if (-not (Test-Path $Blockout)) {
    throw "Expected blockout map was not generated: $Blockout"
}

Write-Host "[NARIS] W04_AshenForest_Blockout authored successfully"
Write-Host "[NARIS] This is NOT the Shipping map; Shipping requires W04_AshenForest."
