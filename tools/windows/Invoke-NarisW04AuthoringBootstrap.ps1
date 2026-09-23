param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT
)

$ErrorActionPreference = "Stop"

if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

$UProject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Script = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_bootstrap_w04_smoke.py"
$UnrealCmd = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

foreach ($path in @($UProject, $Script, $UnrealCmd)) {
    if (-not (Test-Path $path)) {
        throw "Required path missing: $path"
    }
}

Write-Host "[NARIS] Creating/loading W04_Prototype editor smoke map"
& $UnrealCmd $UProject "-ExecutePythonScript=$Script" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) {
    throw "W04 editor bootstrap failed with exit code $LASTEXITCODE"
}

Write-Host "[NARIS] W04 editor bootstrap completed"
