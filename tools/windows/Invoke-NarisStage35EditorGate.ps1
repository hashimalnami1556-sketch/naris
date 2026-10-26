param(
 [Parameter(Mandatory=$true)][string]$RepoRoot,
 [Parameter(Mandatory=$true)][string]$UnrealEngineRoot
)
$ErrorActionPreference='Stop'
$project=Join-Path $RepoRoot 'unreal\NARIS_W04\NARIS_W04.uproject'
$build=Join-Path $UnrealEngineRoot 'Engine\Build\BatchFiles\Build.bat'
$editor=Join-Path $UnrealEngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$script=Join-Path $RepoRoot 'unreal\NARIS_W04\Content\Python\naris_stage35_asset_gate.py'
foreach($p in @($project,$build,$editor,$script)){if(!(Test-Path -LiteralPath $p)){throw "Missing required file: $p"}}
$reportDir=Join-Path $RepoRoot 'unreal\NARIS_W04\Saved\TestReports'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$log=Join-Path $reportDir 'stage35_editor_build.log'
& $build NARIS_W04Editor Win64 Development "-Project=$project" -WaitMutex -NoHotReload 2>&1 | Tee-Object -FilePath $log
if($LASTEXITCODE -ne 0){throw "Editor C++ compilation failed: $LASTEXITCODE"}
& $editor $project "-ExecutePythonScript=$script" -unattended -nop4 -nosplash -NullRHI -log 2>&1 | Tee-Object -FilePath (Join-Path $reportDir 'stage35_asset_gate.log')
if($LASTEXITCODE -ne 0){throw "Editor asset audit failed: $LASTEXITCODE"}
$json=Join-Path $reportDir 'stage35_asset_gate.json'
if(!(Test-Path -LiteralPath $json)){throw 'Expected UE asset gate JSON missing'}
$data=Get-Content -LiteralPath $json -Raw | ConvertFrom-Json
if($data.blockers.Count -gt 0){throw ("Asset blockers: " + ($data.blockers -join '; '))}
Write-Host "Stage35 editor build and asset audit passed. PIE/gameplay/shipping NOT tested."
