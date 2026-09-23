param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT
)

$ErrorActionPreference = "Stop"

if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UNREAL_ENGINE_ROOT is not configured or does not exist."
}

$UProject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Config = Join-Path $RepoRoot "unreal\NARIS_W04\Config\Localization\NARIS_Game.ini"
$UnrealCmd = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

foreach ($path in @($UProject, $Config, $UnrealCmd)) {
    if (-not (Test-Path $path)) { throw "Required path missing: $path" }
}

Push-Location (Join-Path $RepoRoot "unreal\NARIS_W04")
try {
    & $UnrealCmd $UProject -run=GatherText "-config=$Config" -unattended -nop4 -stdout -FullStdOutLogOutput
    if ($LASTEXITCODE -ne 0) {
        throw "NARIS localization pipeline failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

Write-Host "[NARIS] Localization gather/import/export/compile completed"
