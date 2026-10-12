param(
    [string]$ProjectRoot = "C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57",
    [string]$UnrealEngineRoot = "C:\Program Files\Epic Games\UE_5.7"
)

$ErrorActionPreference = "Stop"
$env:ComSpec = "C:\Windows\System32\cmd.exe"
$env:SHELL = $env:ComSpec

$UProject = Join-Path $ProjectRoot "NARIS.uproject"
$Source = Join-Path $ProjectRoot "Source\NARIS\NarisCharacter.cpp"
$ReportDir = Join-Path $ProjectRoot "Reports"
$BackupDir = Join-Path $ReportDir "Backups"
$GateAPath = Join-Path $ReportDir "P0-04A_hero_technical_qa.json"
$GateBPath = Join-Path $ReportDir "P0-04B_runtime_qa.json"
$DecisionPath = Join-Path $ReportDir "P0-04B_visual_decision.json"
$ScreenshotPath = Join-Path $ReportDir "P0-04B_HeroCompare.png"
$PromotionReport = Join-Path $ReportDir "P0-05_hero_promotion.json"
$EditorQaLog = Join-Path $ReportDir "P0-05_editor_combat.log"
$PackagedQaLog = Join-Path $ReportDir "P0-05_packaged_combat.log"

$UBT = Join-Path $UnrealEngineRoot "Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
$EditorCmd = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$UAT = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\RunUAT.bat"
$ArchiveRoot = Join-Path $ProjectRoot "Builds\NARIS_Win64_Dev"
$PackagedExe = Join-Path $ArchiveRoot "Windows\NARIS.exe"
$MainMap = "/Game/NARIS/Maps/L_AshMap_Assembly"

$OldAsset = "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3.SK_NARIS_AshenVessel_v3"
$NewAsset = "/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production.SK_NARIS_AshenVessel_Production"

foreach ($Path in @($UProject,$Source,$GateAPath,$GateBPath,$DecisionPath,$ScreenshotPath,$UBT,$EditorCmd,$UAT)) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "P0-05 required path missing: $Path" }
}

$GateA = Get-Content -Raw -LiteralPath $GateAPath | ConvertFrom-Json
$GateB = Get-Content -Raw -LiteralPath $GateBPath | ConvertFrom-Json
$Decision = Get-Content -Raw -LiteralPath $DecisionPath | ConvertFrom-Json

if ($GateA.status -ne "PASS" -or $GateA.technical_acceptance -ne $true) {
    throw "P0-04A technical gate is not approved."
}
if ($GateB.status -ne "PASS_EVIDENCE_READY" -or $GateB.technical_runtime_gate -ne $true -or $GateB.combat_pass -ne $true) {
    throw "P0-04B runtime gate is not ready."
}
if ($Decision.status -ne "APPROVED" -or $Decision.approved -ne $true) {
    throw "P0-04B visual decision is not APPROVED."
}

$ActualShotHash = (Get-FileHash -LiteralPath $ScreenshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
$ExpectedShotHash = [string]$Decision.screenshot_sha256
if (-not $ExpectedShotHash -or $ActualShotHash -ne $ExpectedShotHash.ToLowerInvariant()) {
    throw "Visual approval hash does not match current screenshot."
}

New-Item -ItemType Directory -Force $BackupDir | Out-Null
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Backup = Join-Path $BackupDir ("NarisCharacter_pre_P0_05_" + $Timestamp + ".cpp")
Copy-Item -LiteralPath $Source -Destination $Backup -Force

$Promoted = $false
$RollbackDone = $false
$Failure = $null

function Assert-CombatQa {
    param([string]$LogPath,[string]$Label)
    if (-not (Test-Path -LiteralPath $LogPath)) { throw "$Label log missing: $LogPath" }
    $Text = Get-Content -Raw -LiteralPath $LogPath
    if ($Text -notmatch "NARIS_COMBAT_QA_RESULT Pass=1") { throw "$Label combat QA did not pass." }
    foreach ($Pattern in @("Fatal error:","Unhandled Exception","Assertion failed:","LowLevelFatalError","Ensure condition failed:")) {
        if ($Text.Contains($Pattern)) { throw "$Label contains fatal runtime marker: $Pattern" }
    }
}

try {
    $SourceText = Get-Content -Raw -LiteralPath $Source
    if ($SourceText.Contains($NewAsset)) {
        Write-Host "[P0-05] Candidate path already active."
    } elseif ($SourceText.Contains($OldAsset)) {
        $SourceText = $SourceText.Replace($OldAsset,$NewAsset)
        Set-Content -LiteralPath $Source -Value $SourceText -Encoding UTF8
    } else {
        throw "Neither expected HeroV3 nor HeroProduction asset path exists in NarisCharacter.cpp."
    }

    Write-Host "[P0-05] Building NARISEditor after hero promotion"
    & $UBT "NARISEditor" "Win64" "Development" "-Project=$UProject" "-WaitMutex" "-NoHotReloadFromIDE"
    if ($LASTEXITCODE -ne 0) { throw "NARISEditor build failed: $LASTEXITCODE" }

    if (Test-Path -LiteralPath $EditorQaLog) { Remove-Item -LiteralPath $EditorQaLog -Force }
    Write-Host "[P0-05] Running D3D12 editor combat regression"
    $EditorArgs = @(
        $UProject,$MainMap,"-game","-unattended","-nop4","-nosplash",
        "-windowed","-ResX=1280","-ResY=720","-NARISCOMBATQA","-abslog=$EditorQaLog"
    )
    & $EditorCmd @EditorArgs
    if ($LASTEXITCODE -ne 0) { throw "Editor combat QA process failed: $LASTEXITCODE" }
    Assert-CombatQa -LogPath $EditorQaLog -Label "Editor"

    Write-Host "[P0-05] Building NARIS Win64 Development"
    & $UBT "NARIS" "Win64" "Development" "-Project=$UProject" "-WaitMutex" "-NoHotReloadFromIDE"
    if ($LASTEXITCODE -ne 0) { throw "NARIS game build failed: $LASTEXITCODE" }

    Write-Host "[P0-05] Cook Stage Pak Archive"
    $UatArgs = @(
        "BuildCookRun",
        "-project=$UProject",
        "-noP4",
        "-platform=Win64",
        "-clientconfig=Development",
        "-skipbuild",
        "-cook",
        "-stage",
        "-pak",
        "-archive",
        "-archivedirectory=$ArchiveRoot",
        "-map=$MainMap",
        "-unattended",
        "-utf8output"
    )
    & $UAT @UatArgs
    if ($LASTEXITCODE -ne 0) { throw "BuildCookRun failed: $LASTEXITCODE" }
    if (-not (Test-Path -LiteralPath $PackagedExe)) { throw "Packaged NARIS.exe not found." }

    if (Test-Path -LiteralPath $PackagedQaLog) { Remove-Item -LiteralPath $PackagedQaLog -Force }
    Write-Host "[P0-05] Running packaged combat regression"
    $Proc = Start-Process -FilePath $PackagedExe -ArgumentList @(
        "-unattended","-nosplash","-windowed","-ResX=1280","-ResY=720",
        "-NARISCOMBATQA","-abslog=$PackagedQaLog"
    ) -PassThru
    if (-not $Proc.WaitForExit(90000)) {
        Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
        throw "Packaged combat QA timed out."
    }
    if ($Proc.ExitCode -ne 0) { throw "Packaged combat QA exited with $($Proc.ExitCode)" }
    Assert-CombatQa -LogPath $PackagedQaLog -Label "Packaged"

    $Promoted = $true
} catch {
    $Failure = $_.Exception.Message
    Write-Warning "[P0-05] Promotion failed: $Failure"
    Copy-Item -LiteralPath $Backup -Destination $Source -Force
    $RollbackDone = $true
    try {
        & $UBT "NARISEditor" "Win64" "Development" "-Project=$UProject" "-WaitMutex" "-NoHotReloadFromIDE"
    } catch {}
}

$Result = [ordered]@{
    schema = "naris.p0.hero-promotion.v1"
    status = if ($Promoted) { "PASS" } else { "FAIL_ROLLED_BACK" }
    product = "CALL OF NARIS"
    old_asset = $OldAsset
    promoted_asset = $NewAsset
    screenshot_sha256 = $ActualShotHash
    visual_decision = $Decision.status
    editor_combat_pass = $Promoted
    packaged_combat_pass = $Promoted
    source_backup = $Backup
    rollback_done = $RollbackDone
    failure = $Failure
    replacement_allowed = $Promoted
}
$Result | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $PromotionReport -Encoding UTF8
Write-Host ($Result | ConvertTo-Json -Depth 7)

if (-not $Promoted) { throw "P0-05 promotion failed and source was rolled back." }
Write-Host "[P0-05] PASS: HeroProduction is now the active master hero and packaged combat QA passed."