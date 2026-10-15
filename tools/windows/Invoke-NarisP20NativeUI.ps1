<#
.SYNOPSIS
  Safely build and optionally launch the CALL OF NARIS W04 native P20 HUD.
.DESCRIPTION
  Requires source already checked out. NEVER copies P20 browser HTML into
  Content, never writes into NARIS_UE57, and never kills an editor process.
  A failed preflight does not modify the project.
.EXAMPLE
  pwsh -File tools/windows/Invoke-NarisP20NativeUI.ps1 -Launch
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$ProjectRoot = '',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [switch]$Launch
)
$ErrorActionPreference = 'Stop'
if (-not $ProjectRoot) {
    $ProjectRoot = Join-Path $RepoRoot 'unreal\NARIS_W04'
}
$ProjectRoot = [IO.Path]::GetFullPath($ProjectRoot)
$uproject = Join-Path $ProjectRoot 'NARIS_W04.uproject'
$build = Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$source = Join-Path $ProjectRoot 'Source\NARIS_W04\Private\NarisHUD.cpp'

foreach ($path in @($uproject, $build, $source)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "P20 PREFLIGHT FAILED: required file missing: $path"
    }
}
if ($ProjectRoot -match 'NARIS_UE57') {
    throw 'P20 W04 source is incompatible with the separate NARIS_UE57 project without a targeted integration.'
}
if ((Get-Content -LiteralPath $source -Raw) -notmatch 'P20 native combat HUD') {
    throw 'P20 source signature not found. Checkout the P20 integration branch.'
}
if (Get-Process -Name UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'Unreal Editor is running. Close it manually before compiling; the script will not terminate it.'
}
if ($Launch) {
    if (-not (Test-Path -LiteralPath $editor -PathType Leaf)) {
        throw "P20 PREFLIGHT FAILED: UnrealEditor.exe missing at $editor"
    }
    $map = @(Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'Content') -Filter '*.umap' -File -Recurse -ErrorAction SilentlyContinue |
        Select-Object -First 1)
    if ($map.Count -eq 0) {
        throw 'P20 PREFLIGHT FAILED: no playable .umap in W04 Content; no engine launch attempted.'
    }
}
Write-Host '[P20] Preflight passed. Building NARIS_W04Editor for Win64 Development.'
& $build 'NARIS_W04Editor' 'Win64' 'Development' ('-Project=' + $uproject) '-WaitMutex' '-NoHotReloadFromIDE'
if ($LASTEXITCODE -ne 0) {
    throw "P20 Unreal build failed with exit code $LASTEXITCODE"
}
Write-Host '[P20] Native source compiled. This is not a playtest result.'
if (-not $Launch) { return }
$arguments = @('"' + $uproject + '"', '-game', '-windowed', '-ResX=1280', '-ResY=720', '-log', '-NarisSkipFrontEnd')
# Remove the skip flag: the launch must open the P20 front-end, not bypass it.
$arguments = $arguments | Where-Object { $_ -ne '-NarisSkipFrontEnd' }
$process = Start-Process -FilePath $editor -ArgumentList $arguments -PassThru
Start-Sleep -Seconds 10
$process.Refresh()
if ($process.HasExited) {
    throw "P20 Unreal process exited early with code $($process.ExitCode); inspect Saved/Logs."
}
Write-Host ("[P20] Unreal process PID={0}; visual/functional playtest remains necessary." -f $process.Id)
