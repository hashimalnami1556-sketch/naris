<#
.SYNOPSIS
  Install the candidate CALL OF NARIS P20 W04 project to a separate folder
  and launch it using UE 5.7 after native compile and DEV smoke-map bootstrap.

.DESCRIPTION
  Does not modify the existing NARIS_UE57 production project.
  Requires network access, Git, UE 5.7, and a Windows user session with GPU.
  Does not guarantee that content assets are production-complete.
.EXAMPLE
  .\tools\windows\Install-Run-NarisP20-W04.ps1
#>
[CmdletBinding()]
param(
    [string]$InstallRoot = (Join-Path $env:USERPROFILE 'NARIS_P20_W04'),
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [string]$Ref = 'feature/p20-native-ui-20261015'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$RepoURL = 'https://github.com/hashimalnami1556-sketch/naris.git'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required. Install Git for Windows before this launcher can install P20.'
}
$BuildBat = Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat'
if (-not (Test-Path -LiteralPath $BuildBat -PathType Leaf)) {
    throw "UE 5.7 Build.bat was not found: $BuildBat"
}
$InstallRoot = [IO.Path]::GetFullPath($InstallRoot)
$ProductionRoot = Join-Path $env:USERPROFILE 'OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57'
if ($InstallRoot.TrimEnd('\') -ieq $ProductionRoot.TrimEnd('\')) {
    throw 'Refusing to use the separate production project directory.'
}
if (Test-Path -LiteralPath $InstallRoot) {
    if (-not (Test-Path -LiteralPath (Join-Path $InstallRoot '.git') -PathType Container)) {
        throw "Install folder exists but is not a Git checkout: $InstallRoot"
    }
    $Changes = @(git -C $InstallRoot status --porcelain)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read existing Git working tree.' }
    if ($Changes.Count -gt 0) {
        throw 'Existing P20 checkout has local changes/Unreal assets; refusing to overwrite. Use a new -InstallRoot.'
    }
    & git -C $InstallRoot fetch origin $Ref
    if ($LASTEXITCODE -ne 0) { throw 'Git fetch failed.' }
    & git -C $InstallRoot switch $Ref
    if ($LASTEXITCODE -ne 0) { throw 'Cannot switch to P20 branch.' }
    & git -C $InstallRoot merge --ff-only 'FETCH_HEAD'
    if ($LASTEXITCODE -ne 0) { throw 'Git fast-forward failed; project not modified further.' }
} else {
    $Parent = Split-Path -Parent $InstallRoot
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    & git clone --single-branch --branch $Ref --depth 1 $RepoURL $InstallRoot
    if ($LASTEXITCODE -ne 0) { throw 'Git clone of NARIS P20 branch failed.' }
}

$ProjectRoot = Join-Path $InstallRoot 'unreal\NARIS_W04'
$Source = Join-Path $ProjectRoot 'Source\NARIS_W04\Private\NarisHUD.cpp'
$Helper = Join-Path $InstallRoot 'tools\windows\Invoke-NarisP20NativeUI.ps1'
if (-not (Test-Path -LiteralPath $Helper -PathType Leaf) -or
    -not (Test-Path -LiteralPath $Source -PathType Leaf) -or
    (Get-Content -LiteralPath $Source -Raw) -notmatch 'P20 native combat HUD') {
    throw 'P20 native sources were not retrieved as expected.'
}
Write-Host "[P20] Source present in isolated folder: $InstallRoot"
Write-Host '[P20] Compiling native W04, authoring DEV map if needed, and starting Unreal.'
& $Helper -RepoRoot $InstallRoot -ProjectRoot $ProjectRoot -EngineRoot $EngineRoot -BootstrapIfMissing -Launch
Write-Host '[P20] Helper returned. A live game window and playtest still require user-side verification.'
