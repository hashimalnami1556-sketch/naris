[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Project,
    [Parameter(Mandatory=$true)][string]$EngineRoot,
    [Parameter(Mandatory=$true)][string]$Map,
    [Parameter(Mandatory=$true)][string]$AssetDir,
    [string]$Python = 'python',
    [string]$OutputRoot = (Join-Path $PSScriptRoot '../Builds')
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$runId = [guid]::NewGuid().ToString('N')
$runDir = Join-Path $OutputRoot $runId
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
$runDir = (Resolve-Path $runDir).Path
$reportPath = Join-Path $runDir 'build_result.json'
$result = @{ run_id=$runId; verified=$false; scope='windows-package-only'; steps=@(); runtime_tested=$false }
$savedEnvironment = @{}
function Invoke-Step([string]$Name, [string]$Executable, [string[]]$Arguments) {
    $log = Join-Path $runDir ($Name + '.log')
    & $Executable @Arguments *> $log
    $code = $LASTEXITCODE
    $result.steps += @{ name=$Name; exit_code=$code; log=$log }
    if ($code -ne 0) { throw "$Name failed with exit code $code. See $log" }
}
try {
    $Project = (Resolve-Path -LiteralPath $Project).Path
    $EngineRoot = (Resolve-Path -LiteralPath $EngineRoot).Path
    $AssetDir = (Resolve-Path -LiteralPath $AssetDir).Path
    $delivery = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    Invoke-Step 'preflight' $Python @((Join-Path $PSScriptRoot 'validate_project.py'),
        '--project', $Project, '--engine', $EngineRoot, '--map', $Map,
        '--report', (Join-Path $runDir 'preflight.json'))
    $preflight = Get-Content -LiteralPath (Join-Path $runDir 'preflight.json') -Raw | ConvertFrom-Json
    $build = Join-Path $EngineRoot 'Engine/Build/BatchFiles/Build.bat'
    $uat = Join-Path $EngineRoot 'Engine/Build/BatchFiles/RunUAT.bat'
    $editor = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
    foreach ($file in @($build, $uat, $editor)) {
        if (!(Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing tool: $file" }
    }
    Invoke-Step 'editor-build' $build @($preflight.editor_target, 'Win64', 'Development',
        "-Project=$Project", '-WaitMutex', '-NoHotReloadFromIDE')
    foreach ($name in @('NARIS_ASSET_DIR','NARIS_IMPORT_REPORT','NARIS_IMPORT_RUN_ID')) {
        $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    }
    $env:NARIS_ASSET_DIR = $AssetDir
    $env:NARIS_IMPORT_REPORT = Join-Path $runDir 'import_result.json'
    $env:NARIS_IMPORT_RUN_ID = $runId
    Invoke-Step 'import' $editor @($Project, '-unattended', '-nop4', '-NullRHI',
        '-run=pythonscript', "-script=$(Join-Path $delivery 'Unreal/import_and_verify.py')")
    if (!(Test-Path -LiteralPath $env:NARIS_IMPORT_REPORT)) { throw 'Editor produced no import report' }
    $import = Get-Content -LiteralPath $env:NARIS_IMPORT_REPORT -Raw | ConvertFrom-Json
    if ($import.verified -ne $true -or $import.run_id -ne $runId -or @($import.results).Count -eq 0) {
        throw 'Import report failed, is empty or belongs to another run'
    }
    $archive = Join-Path $runDir 'Archive'
    Invoke-Step 'package' $uat @('BuildCookRun', "-project=$Project", '-noP4', '-utf8output',
        '-platform=Win64', '-clientconfig=Development', '-build', '-cook', "-map=$Map",
        '-stage', '-pak', '-package', '-archive', "-archivedirectory=$archive", '-unattended')
    $artifactReport = Join-Path $runDir 'package_artifacts.json'
    Invoke-Step 'package-artifacts' $Python @((Join-Path $PSScriptRoot 'verify_package.py'),
        '--archive', $archive, '--project-name', [IO.Path]::GetFileNameWithoutExtension($Project),
        '--report', $artifactReport)
    $artifacts = Get-Content -LiteralPath $artifactReport -Raw | ConvertFrom-Json
    if ($artifacts.verified -ne $true) { throw 'Packaged game artifacts failed validation' }
    $result.artifacts = $artifacts.artifacts
    $result.verified = $true
} catch {
    $result.error = $_.Exception.Message
    throw
} finally {
    foreach ($name in $savedEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')
    }
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Host "Build evidence: $reportPath"
}
