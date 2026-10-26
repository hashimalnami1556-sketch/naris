param(
  [string]$EngineRoot = "C:\Program Files\Epic Games\UE_5.7",
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
  [ValidateSet("Development","Shipping")][string]$Configuration = "Shipping"
)
$ErrorActionPreference="Stop"
$Project=Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$EditorCmd=Join-Path $EngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$UAT=Join-Path $EngineRoot "Engine\Build\BatchFiles\RunUAT.bat"
$FinalMap="/Game/NARIS/W04/Maps/W04_AshenForest"
$MapFile=Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Maps\W04_AshenForest.umap"
$Archive=Join-Path $RepoRoot ("Builds\Windows_"+$Configuration)
if(!(Test-Path $Project)){throw "Missing project: $Project"}
if(!(Test-Path $EditorCmd)){throw "Missing UnrealEditor-Cmd: $EditorCmd"}
if(!(Test-Path $UAT)){throw "Missing RunUAT: $UAT"}
if(!(Test-Path $MapFile)){throw "FINAL MAP GATE FAILED: W04_AshenForest.umap is not authored/saved yet. Shipping is blocked."}
& $EditorCmd $Project $FinalMap -run=NarisValidateShippingMap -unattended -nop4 -nosplash -NullRHI
if($LASTEXITCODE -ne 0){throw "Shipping map validation failed."}
& $UAT BuildCookRun -project="$Project" -noP4 -platform=Win64 -clientconfig=$Configuration -build -cook -stage -pak -package -archive -archivedirectory="$Archive" -map="$FinalMap" -utf8output
if($LASTEXITCODE -ne 0){throw "BuildCookRun failed: $LASTEXITCODE"}
$exe=Get-ChildItem $Archive -Filter "*.exe" -Recurse | Where-Object {$_.Name -match "NARIS"} | Select-Object -First 1
if(!$exe){throw "PACKAGE GATE FAILED: no NARIS Windows executable found."}
$hash=(Get-FileHash $exe.FullName -Algorithm SHA256).Hash
Write-Host "[NARIS] WINDOWS PACKAGE PASS"
Write-Host "[NARIS] EXE: $($exe.FullName)"
Write-Host "[NARIS] SHA256: $hash"
