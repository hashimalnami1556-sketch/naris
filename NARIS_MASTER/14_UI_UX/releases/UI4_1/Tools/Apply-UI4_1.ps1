param(
 [string]$ProjectRoot='C:\Users\Admin\NARIS',
 [string]$EngineRoot='C:\Program Files\Epic Games\UE_5.7'
)
$ErrorActionPreference='Stop'
$uproject=Join-Path $ProjectRoot 'NARIS.uproject'
$hudH=Join-Path $ProjectRoot 'Source\NarisCore\Public\NarisHUD.h'
$hudC=Join-Path $ProjectRoot 'Source\NarisCore\Private\NarisHUD.cpp'
$gmC=Join-Path $ProjectRoot 'Source\NarisCore\Private\NarisGameModeBase.cpp'
$input=Join-Path $ProjectRoot 'Config\DefaultInput.ini'
foreach($f in @($uproject,$hudH,$hudC,$gmC,$input)){if(!(Test-Path $f)){throw "Required file missing: $f"}}

$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
$backup=Join-Path $ProjectRoot "Backups\UI4_1\$stamp"
New-Item -ItemType Directory -Force $backup | Out-Null
Copy-Item $hudH (Join-Path $backup 'NarisHUD.h')
Copy-Item $hudC (Join-Path $backup 'NarisHUD.cpp')
Copy-Item $gmC (Join-Path $backup 'NarisGameModeBase.cpp')
Copy-Item $input (Join-Path $backup 'DefaultInput.ini')

$gm=Get-Content -Raw $gmC
if($gm -notmatch 'NarisDirectPlay'){throw 'Explicit DirectPlay flag marker missing. Refusing unsafe patch.'}
if($gm -match 'bSmoke\|\|!bFrontEnd'){throw 'Direct-play regression detected in GameMode.'}

$ini=Get-Content -Raw $input
if($ini -notmatch '(?m)^\+ActionMappings=\(ActionName="Resonance"[^\r\n]*Key=R\)'){
 $mapping='+ActionMappings=(ActionName="Resonance",bShift=False,bCtrl=False,bAlt=False,bCmd=False,Key=R)'
 $ini=$ini.TrimEnd() + [Environment]::NewLine + $mapping + [Environment]::NewLine
 Set-Content $input $ini -Encoding UTF8
}

$hc=Get-Content -Raw $hudC
foreach($marker in @('StartGame','ContinueGame','OpenSettings','ExitGame','CALL OF NARIS')){
 if($hc -notmatch [regex]::Escape($marker)){throw "HUD marker missing: $marker"}
}

$ubt=Join-Path $EngineRoot 'Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe'
$uat=Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
if(!(Test-Path $ubt)){throw "UBT missing: $ubt"}
if(!(Test-Path $uat)){throw "UAT missing: $uat"}

Get-Process UnrealEditor -ErrorAction SilentlyContinue | Stop-Process -Force
& $ubt NARISEditor Win64 Development "-Project=$uproject" -NoHotReloadFromIDE
if($LASTEXITCODE -ne 0){throw "NARISEditor build failed: $LASTEXITCODE"}

$out=Join-Path $ProjectRoot 'Builds\WindowsDevelopment_UI4_1'
if(Test-Path $out){throw "Target build directory already exists; preserving it: $out"}
New-Item -ItemType Directory -Force $out | Out-Null
& $uat BuildCookRun "-project=$uproject" -noP4 -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive "-archivedirectory=$out" -utf8output
if($LASTEXITCODE -ne 0){throw "Packaging failed: $LASTEXITCODE"}

$exe=Join-Path $out 'NARIS.exe'
if(!(Test-Path $exe)){throw "Packaged EXE missing: $exe"}
Start-Process $exe -ArgumentList '-windowed','-ResX=1280','-ResY=720','-log'
Start-Sleep 8
& (Join-Path $PSScriptRoot 'Validate-UI4_1.ps1') -ProjectRoot $ProjectRoot
if($LASTEXITCODE -ne 0){throw "Packaged runtime validation failed: $LASTEXITCODE"}
