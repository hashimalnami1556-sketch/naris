param(
  [string]$ProjectRoot = "C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57",
  [switch]$SkipPackage
)

$ErrorActionPreference = "Stop"
$UE  = "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$UBT = "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
$UAT = "C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\RunUAT.bat"

$Project       = Join-Path $ProjectRoot "NARIS.uproject"
$Source        = Join-Path $ProjectRoot "Source\NARIS\NarisCharacter.cpp"
$Report4B      = Join-Path $ProjectRoot "Reports\P0-04B_runtime_candidate_qa.json"
$VisualDecision= Join-Path $ProjectRoot "Reports\P0-04B_visual_decision.json"
$Report5       = Join-Path $ProjectRoot "Reports\P0-05_hero_promotion.json"
$EditorLog     = Join-Path $ProjectRoot "Reports\P0-05_editor_runtime.log"
$Archive       = Join-Path $ProjectRoot "Builds\NARIS_Win64_Dev"
$PackagedExe   = Join-Path $Archive "Windows\NARIS.exe"
$PackagedLog   = Join-Path $Archive "Windows\NARIS\Saved\Logs\NARIS.log"
$Backup        = Join-Path $ProjectRoot "Reports\Backups\NarisCharacter_pre_P0-05.cpp"

$OldAsset       = "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3.SK_NARIS_AshenVessel_v3"
$CandidateAsset = "/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production.SK_NARIS_AshenVessel_Production"

function Write-Result([hashtable]$Data) {
  New-Item -ItemType Directory -Force (Split-Path $Report5 -Parent) | Out-Null
  ($Data | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $Report5 -Encoding UTF8
}
function Require-Path([string]$PathToCheck) {
  if (-not (Test-Path -LiteralPath $PathToCheck)) { throw "Missing required path: $PathToCheck" }
}
function Parse-RuntimeLog([string]$LogPath) {
  if (-not (Test-Path -LiteralPath $LogPath)) {
    return @{ exists=$false; pass=$false; fatal=999; missing=999; anim=999; qa_line=$null }
  }
  $lines = Get-Content -LiteralPath $LogPath
  $qa = $lines | Select-String -SimpleMatch "NARIS_COMBAT_QA_RESULT" | Select-Object -Last 1
  return @{
    exists  = $true
    pass    = ($null -ne $qa -and $qa.Line -match "Pass=1")
    qa_line = if ($qa) { $qa.Line } else { $null }
    fatal   = @($lines | Select-String -SimpleMatch "Fatal error").Count
    missing = @($lines | Select-String -Pattern "Failed to load|Failed to find|Missing skeletal|Can't find file").Count
    anim    = @($lines | Select-String -Pattern "Animation.*Skeleton|incompatible skeleton|different skeleton").Count
  }
}

foreach ($p in @($UE,$UBT,$Project,$Source,$Report4B,$VisualDecision)) { Require-Path $p }

$p4b = Get-Content -Raw -LiteralPath $Report4B | ConvertFrom-Json
if ($p4b.status -ne "PASS" -or $p4b.runtime_acceptance -ne $true) {
  Write-Result @{ status="FAIL"; reason="P0-04B_runtime_not_passed"; promotion_applied=$false }
  throw "P0-04B runtime acceptance missing"
}

$decision = Get-Content -Raw -LiteralPath $VisualDecision | ConvertFrom-Json
if ($decision.accepted -ne $true) {
  Write-Result @{ status="FAIL"; reason="visual_acceptance_not_granted"; promotion_applied=$false }
  throw "Visual acceptance is required"
}
if (-not $p4b.screenshot) {
  Write-Result @{ status="FAIL"; reason="P0-04B_has_no_screenshot"; promotion_applied=$false }
  throw "P0-04B screenshot missing"
}
Require-Path ([string]$p4b.screenshot)

$actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath ([string]$p4b.screenshot)).Hash.ToLowerInvariant()
$approvedHash = ([string]$decision.screenshot_sha256).ToLowerInvariant()
if ([string]::IsNullOrWhiteSpace($approvedHash) -or $actualHash -ne $approvedHash) {
  Write-Result @{
    status="FAIL"; reason="visual_decision_hash_mismatch"; actual_sha256=$actualHash;
    approved_sha256=$approvedHash; promotion_applied=$false
  }
  throw "Visual acceptance does not match the QA screenshot"
}

$original = Get-Content -Raw -LiteralPath $Source
if (-not $original.Contains($OldAsset)) {
  Write-Result @{ status="FAIL"; reason="working_asset_path_not_found"; promotion_applied=$false }
  throw "Expected working HeroV3 path not found"
}

New-Item -ItemType Directory -Force (Split-Path $Backup -Parent) | Out-Null
Copy-Item -LiteralPath $Source -Destination $Backup -Force

$promotionApplied = $false
$editorBuild = $false
$gameBuild = $false
$editorRuntime = $null
$packageOk = $false
$packagedRuntime = $null
$restored = $false
$failureReason = $null

try {
  $promoted = $original.Replace($OldAsset,$CandidateAsset)
  Set-Content -LiteralPath $Source -Value $promoted -Encoding UTF8
  $promotionApplied = $true

  & $UBT NARISEditor Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE
  if ($LASTEXITCODE -ne 0) { throw "promoted editor build failed" }
  $editorBuild = $true

  & $UBT NARIS Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE
  if ($LASTEXITCODE -ne 0) { throw "promoted game build failed" }
  $gameBuild = $true

  if (Test-Path $EditorLog) { Remove-Item $EditorLog -Force }
  $editorArgs = @(
    $Project,
    "/Game/NARIS/Maps/L_AshMap_Assembly",
    "-game","-unattended","-nop4","-nosplash",
    "-windowed","-ResX=1280","-ResY=720",
    "-NARISCOMBATQA",
    "-abslog=$EditorLog"
  )
  & $UE @editorArgs
  if ($LASTEXITCODE -ne 0) { throw "promoted editor runtime failed with exit $LASTEXITCODE" }

  $editorRuntime = Parse-RuntimeLog $EditorLog
  if (-not $editorRuntime.pass -or $editorRuntime.fatal -ne 0 -or $editorRuntime.missing -ne 0 -or $editorRuntime.anim -ne 0) {
    throw "promoted editor runtime gate failed"
  }

  if (-not $SkipPackage) {
    $env:ComSpec = "C:\Windows\System32\cmd.exe"
    $env:SHELL = $env:ComSpec
    $uatArgs = @(
      "BuildCookRun",
      "-project=$Project",
      "-noP4",
      "-platform=Win64",
      "-clientconfig=Development",
      "-skipbuild",
      "-cook",
      "-iterativecooking",
      "-stage",
      "-pak",
      "-archive",
      "-archivedirectory=$Archive",
      "-map=/Game/NARIS/Maps/L_AshMap_Assembly",
      "-unattended",
      "-utf8output"
    )
    & $UAT @uatArgs
    if ($LASTEXITCODE -ne 0) { throw "promoted package failed" }
    $packageOk = $true

    Require-Path $PackagedExe
    if (Test-Path $PackagedLog) { Remove-Item $PackagedLog -Force }
    $packArgs = @("-unattended","-nosplash","-windowed","-ResX=1280","-ResY=720","-NARISCOMBATQA","-log")
    & $PackagedExe @packArgs
    $packExit = $LASTEXITCODE
    Start-Sleep -Seconds 2
    $packagedRuntime = Parse-RuntimeLog $PackagedLog
    if ($packExit -ne 0 -or -not $packagedRuntime.pass -or
        $packagedRuntime.fatal -ne 0 -or $packagedRuntime.missing -ne 0 -or $packagedRuntime.anim -ne 0) {
      throw "promoted packaged runtime gate failed"
    }
  } else {
    $packageOk = $true
  }
}
catch {
  $failureReason = $_.Exception.Message
}
finally {
  if ($failureReason) {
    Write-Warning "[P0-05] Promotion failed; restoring HeroV3 source."
    Copy-Item -LiteralPath $Backup -Destination $Source -Force
    $restored = $true
    try { & $UBT NARISEditor Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE | Out-Host } catch {}
    try { & $UBT NARIS Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE | Out-Host } catch {}
    $promotionApplied = $false
  }
}

$runtimeEditorPass = ($null -ne $editorRuntime -and $editorRuntime.pass)
$runtimePackPass = ($SkipPackage -or ($null -ne $packagedRuntime -and $packagedRuntime.pass))
$passed = (-not $failureReason) -and $promotionApplied -and $editorBuild -and $gameBuild -and
          $runtimeEditorPass -and $packageOk -and $runtimePackPass

$result = @{
  status = if ($passed) { "PASS" } else { "FAIL_REVERTED" }
  promotion_applied = $passed
  candidate_asset = $CandidateAsset
  previous_asset = $OldAsset
  screenshot_sha256 = $actualHash
  visual_decision = $decision
  editor_build = $editorBuild
  game_build = $gameBuild
  editor_runtime = $editorRuntime
  package_ok = $packageOk
  packaged_runtime = $packagedRuntime
  source_restored_after_failure = $restored
  failure_reason = $failureReason
  final_policy = if ($passed) { "HeroProduction promoted; keep HeroV3 backup for rollback" } else { "HeroV3 retained" }
}
Write-Result $result
$result | ConvertTo-Json -Depth 10 | Write-Host
if (-not $passed) { exit 70 }
exit 0
