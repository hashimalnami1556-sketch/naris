param(
 [string]$EngineRoot="C:\Program Files\Epic Games\UE_5.7",
 [string]$RepoRoot=(Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)
$ErrorActionPreference="Stop"
$Runtime=Join-Path $RepoRoot "tools\windows\Invoke-NarisStage30Runtime.ps1"
$Shipping=Join-Path $RepoRoot "tools\windows\Build-NarisWindows.ps1"
if(!(Test-Path $Runtime)){throw "Missing Stage30 runtime runner"}
if(!(Test-Path $Shipping)){throw "Missing Windows shipping runner"}
Write-Host "[Stage32] Gate A: UE5.7 compile/assets/map"
& $Runtime -EngineRoot $EngineRoot -RepoRoot $RepoRoot
if($LASTEXITCODE -ne 0){throw "Stage32 runtime gate failed"}
Write-Host "[Stage32] Gate B: Shipping package"
& $Shipping -EngineRoot $EngineRoot -RepoRoot $RepoRoot -Configuration Shipping
if($LASTEXITCODE -ne 0){throw "Stage32 shipping gate failed"}
Write-Host "[Stage32] Automated gates complete. Interactive PIE, visual PBR and packaged playthrough evidence remain required before release approval."
