param(
  [string]$ProjectRoot = "C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
)

$ErrorActionPreference = "Stop"
$UE = "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$UBT = "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
$Project = Join-Path $ProjectRoot "NARIS.uproject"
$Source = Join-Path $ProjectRoot "Source\NARIS\NarisCharacter.cpp"
$Report4A = Join-Path $ProjectRoot "Reports\P0-04A_hero_technical_qa.json"
$Report4B = Join-Path $ProjectRoot "Reports\P0-04B_runtime_candidate_qa.json"
$RuntimeLog = Join-Path $ProjectRoot "Reports\P0-04B_candidate_runtime.log"
$Backup = Join-Path $ProjectRoot "Reports\Backups\NarisCharacter_pre_P0-04B.cpp"
$ShotOut = Join-Path $ProjectRoot "Reports\P0-04B_candidate.png"

$OldAsset = "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3.SK_NARIS_AshenVessel_v3"
$CandidateAsset = "/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production.SK_NARIS_AshenVessel_Production"

function Write-Result([hashtable]$Data) {
  $dir = Split-Path $Report4B -Parent
  New-Item -ItemType Directory -Force $dir | Out-Null
  ($Data | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $Report4B -Encoding UTF8
}

foreach ($p in @($UE,$UBT,$Project,$Source,$Report4A)) {
  if (-not (Test-Path -LiteralPath $p)) {
    Write-Result @{
      status="FAIL"; reason="missing_required_path"; path=$p;
      runtime_acceptance=$false; visual_acceptance="NOT_RUN"; replacement_allowed=$false
    }
    throw "Missing required path: $p"
  }
}

$p4a = Get-Content -Raw -LiteralPath $Report4A | ConvertFrom-Json
if ($p4a.status -ne "PASS" -or $p4a.technical_acceptance -ne $true) {
  Write-Result @{
    status="FAIL"; reason="P0-04A_not_passed";
    runtime_acceptance=$false; visual_acceptance="NOT_RUN"; replacement_allowed=$false
  }
  throw "P0-04A did not pass"
}

$original = Get-Content -Raw -LiteralPath $Source
if (-not $original.Contains($OldAsset)) {
  Write-Result @{
    status="FAIL"; reason="working_hero_asset_path_not_found";
    expected=$OldAsset; runtime_acceptance=$false; visual_acceptance="NOT_RUN"; replacement_allowed=$false
  }
  throw "Could not find working HeroV3 asset path in NarisCharacter.cpp"
}
if ($original.Contains($CandidateAsset)) {
  Write-Result @{
    status="FAIL"; reason="candidate_already_active_before_trial";
    runtime_acceptance=$false; visual_acceptance="NOT_RUN"; replacement_allowed=$false
  }
  throw "Candidate already active; refusing destructive QA"
}

New-Item -ItemType Directory -Force (Split-Path $Backup -Parent) | Out-Null
Copy-Item -LiteralPath $Source -Destination $Backup -Force

$trialBuildOk=$false
$runtimeExit=-999
$combatPass=$false
$fatalCount=0
$missingAssetCount=0
$animWarningCount=0
$fxSpawnCount=0
$audioCount=0
$screenshot=$null
$restoreBuildOk=$false
$sourceRestored=$false

try {
  Write-Host "[P0-04B] Temporarily activating candidate hero..."
  $trial = $original.Replace($OldAsset,$CandidateAsset)
  Set-Content -LiteralPath $Source -Value $trial -Encoding UTF8

  Write-Host "[P0-04B] Building candidate Editor target..."
  & $UBT NARISEditor Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE
  if ($LASTEXITCODE -ne 0) { throw "Candidate editor build failed: $LASTEXITCODE" }
  $trialBuildOk=$true

  if (Test-Path $RuntimeLog) { Remove-Item $RuntimeLog -Force }

  $before = @{}
  $shotDirs=@(
    (Join-Path $ProjectRoot "Saved\Screenshots\WindowsEditor"),
    (Join-Path $ProjectRoot "Saved\Screenshots\Windows")
  )
  foreach($dir in $shotDirs) {
    if(Test-Path $dir) {
      Get-ChildItem $dir -Filter *.png -File | ForEach-Object { $before[$_.FullName]=$_.LastWriteTimeUtc }
    }
  }

  Write-Host "[P0-04B] Running D3D12 combat trial with candidate..."
  $args=@(
    $Project,
    "/Game/NARIS/Maps/L_AshMap_Assembly",
    "-game","-unattended","-nop4","-nosplash",
    "-windowed","-ResX=1280","-ResY=720",
    "-NARISCOMBATQA",
    "-ExecCmds=HighResShot 1",
    "-abslog=$RuntimeLog"
  )
  & $UE @args
  $runtimeExit=$LASTEXITCODE

  if (-not (Test-Path $RuntimeLog)) { throw "Candidate runtime log missing" }
  $lines=Get-Content -LiteralPath $RuntimeLog

  $combat = $lines | Select-String -SimpleMatch "NARIS_COMBAT_QA_RESULT" | Select-Object -Last 1
  $combatPass = $null -ne $combat -and $combat.Line -match "Pass=1"
  $fatalCount = @($lines | Select-String -SimpleMatch "Fatal error").Count
  $missingAssetCount = @($lines | Select-String -Pattern "Failed to load|Failed to find|Missing skeletal|Can't find file").Count
  $animWarningCount = @($lines | Select-String -Pattern "Animation.*Skeleton|incompatible skeleton|different skeleton").Count
  $fxSpawnCount = @($lines | Select-String -SimpleMatch "NARIS_IMPACT_FX" | Where-Object {$_.Line -match "Spawned=1"}).Count
  $audioCount = @($lines | Select-String -SimpleMatch "NARIS_IMPACT_AUDIO" | Where-Object {$_.Line -match "Played=1"}).Count

  $newShots=@()
  foreach($dir in $shotDirs) {
    if(Test-Path $dir) {
      $newShots += Get-ChildItem $dir -Filter *.png -File |
        Where-Object { -not $before.ContainsKey($_.FullName) -or $_.LastWriteTimeUtc -gt $before[$_.FullName] }
    }
  }
  $latest=$newShots | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
  if($latest) {
    Copy-Item -LiteralPath $latest.FullName -Destination $ShotOut -Force
    $screenshot=$ShotOut
  }
}
catch {
  Write-Warning "[P0-04B] Trial failure: $($_.Exception.Message)"
}
finally {
  Write-Host "[P0-04B] Restoring working HeroV3 source..."
  Copy-Item -LiteralPath $Backup -Destination $Source -Force
  $restored = Get-Content -Raw -LiteralPath $Source
  $sourceRestored = $restored.Contains($OldAsset) -and -not $restored.Contains($CandidateAsset)

  try {
    & $UBT NARISEditor Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE
    $restoreBuildOk = $LASTEXITCODE -eq 0
  }
  catch { $restoreBuildOk=$false }
}

$runtimePass = $trialBuildOk -and ($runtimeExit -eq 0) -and $combatPass -and
               ($fatalCount -eq 0) -and ($missingAssetCount -eq 0) -and
               ($animWarningCount -eq 0) -and $sourceRestored -and $restoreBuildOk

$result=@{
  status = if($runtimePass){"PASS"}else{"FAIL_GATE"}
  candidate_asset=$CandidateAsset
  working_asset_restored=$OldAsset
  trial_build_ok=$trialBuildOk
  runtime_exit_code=$runtimeExit
  combat_pass=$combatPass
  fatal_count=$fatalCount
  missing_asset_count=$missingAssetCount
  animation_compatibility_warning_count=$animWarningCount
  impact_fx_spawn_count=$fxSpawnCount
  impact_audio_play_count=$audioCount
  source_restored=$sourceRestored
  restore_build_ok=$restoreBuildOk
  runtime_acceptance=$runtimePass
  screenshot=$screenshot
  visual_acceptance=if($screenshot){"PENDING_REVIEW"}else{"NO_SCREENSHOT"}
  replacement_allowed=$false
  next_gate="Visual review of P0-04B screenshot, then P0-05 atomic promotion/revert test"
}
Write-Result $result
$result | ConvertTo-Json -Depth 8 | Write-Host

if(-not $runtimePass){ exit 60 }
exit 0
