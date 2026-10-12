param(
    [string]$RepoRoot = "",
    [string]$ProjectRoot = "C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57",
    [string]$UnrealEngineRoot = "C:\Program Files\Epic Games\UE_5.7"
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

$UProject = Join-Path $ProjectRoot "NARIS.uproject"
$EditorCmd = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$EditorGui = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor.exe"
$PrepScript = Join-Path $RepoRoot "tools\unreal\p0_04b_prepare_visual_qa.py"
$ReportA = Join-Path $ProjectRoot "Reports\P0-04A_hero_technical_qa.json"
$SceneReport = Join-Path $ProjectRoot "Reports\P0-04B_visual_scene.json"
$FinalReport = Join-Path $ProjectRoot "Reports\P0-04B_runtime_qa.json"
$CombatLog = Join-Path $ProjectRoot "Reports\P0-04B_combat_d3d12.log"
$ScreenshotOut = Join-Path $ProjectRoot "Reports\P0-04B_HeroCompare.png"
$MainMap = "/Game/NARIS/Maps/L_AshMap_Assembly"
$QaMap = "/Game/NARIS/QA/L_HeroCandidate_QA"

foreach ($Path in @($UProject, $EditorCmd, $EditorGui, $PrepScript, $ReportA)) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "P0-04B required path missing: $Path"
    }
}

$GateA = Get-Content -Raw -LiteralPath $ReportA | ConvertFrom-Json
if ($GateA.status -ne "PASS" -or $GateA.technical_acceptance -ne $true) {
    throw "P0-04A has not passed; refusing P0-04B."
}

Write-Host "[P0-04B] Preparing side-by-side hero QA scene"
$PrepArgs = @(
    $UProject,
    "-unattended",
    "-nop4",
    "-nosplash",
    "-ExecutePythonScript=$PrepScript",
    "-stdout",
    "-FullStdOutLogOutput"
)
& $EditorCmd @PrepArgs
if ($LASTEXITCODE -ne 0) {
    throw "P0-04B visual scene preparation failed with exit code $LASTEXITCODE"
}

if (-not (Test-Path -LiteralPath $SceneReport)) {
    throw "P0-04B visual scene report missing: $SceneReport"
}
$Scene = Get-Content -Raw -LiteralPath $SceneReport | ConvertFrom-Json
if ($Scene.status -ne "PASS" -or $Scene.visual_scene_prepared -ne $true) {
    throw "P0-04B visual scene gate failed."
}

if (Test-Path -LiteralPath $ScreenshotOut) {
    Remove-Item -LiteralPath $ScreenshotOut -Force
}

$CaptureStartedAt = [DateTime]::UtcNow
$RenderArgs = @(
    $UProject,
    $QaMap,
    "-game",
    "-nosplash",
    "-windowed",
    "-ResX=1280",
    "-ResY=720",
    "-NoVSync",
    '-ExecCmds="HighResShot 1"'
)

Write-Host "[P0-04B] Rendering D3D12 hero comparison"
$RenderProcess = Start-Process -FilePath $EditorGui -ArgumentList $RenderArgs -PassThru
Start-Sleep -Seconds 18
if (-not $RenderProcess.HasExited) {
    Stop-Process -Id $RenderProcess.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

$ScreenshotRoots = @(
    (Join-Path $ProjectRoot "Saved\Screenshots\Windows"),
    (Join-Path $ProjectRoot "Saved\Screenshots\WindowsEditor"),
    (Join-Path $ProjectRoot "Saved\Screenshots")
)

$CandidateShots = @()
foreach ($Root in $ScreenshotRoots) {
    if (Test-Path -LiteralPath $Root) {
        $CandidateShots += @(
            Get-ChildItem -Path $Root -Filter "*.png" -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTimeUtc -ge $CaptureStartedAt }
        )
    }
}

$NewestShot = $CandidateShots | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
if ($NewestShot) {
    Copy-Item -LiteralPath $NewestShot.FullName -Destination $ScreenshotOut -Force
}

$ScreenshotPresent = Test-Path -LiteralPath $ScreenshotOut
if (-not $ScreenshotPresent) {
    Write-Warning "P0-04B D3D12 screenshot was not produced."
}

if (Test-Path -LiteralPath $CombatLog) {
    Remove-Item -LiteralPath $CombatLog -Force
}

Write-Host "[P0-04B] Running master D3D12 combat regression"
$CombatArgs = @(
    $UProject,
    $MainMap,
    "-game",
    "-unattended",
    "-nop4",
    "-nosplash",
    "-windowed",
    "-ResX=1280",
    "-ResY=720",
    "-NARISCOMBATQA",
    "-abslog=$CombatLog"
)
& $EditorCmd @CombatArgs
$CombatExit = $LASTEXITCODE

if (-not (Test-Path -LiteralPath $CombatLog)) {
    throw "P0-04B combat log missing: $CombatLog"
}

$CombatText = Get-Content -Raw -LiteralPath $CombatLog
$CombatPass = $CombatText -match "NARIS_COMBAT_QA_RESULT Pass=1"

$FatalPatterns = @(
    "Fatal error:",
    "Unhandled Exception",
    "Assertion failed:",
    "LowLevelFatalError",
    "Ensure condition failed:"
)
$FatalFindings = @()
foreach ($Pattern in $FatalPatterns) {
    $Matches = Select-String -Path $CombatLog -Pattern $Pattern -SimpleMatch -ErrorAction SilentlyContinue
    foreach ($Match in $Matches) {
        $FatalFindings += [ordered]@{
            pattern = $Pattern
            line = $Match.LineNumber
            text = $Match.Line.Trim()
        }
    }
}

$RuntimeGate = ($CombatExit -eq 0 -and $CombatPass -and $FatalFindings.Count -eq 0)

$Result = [ordered]@{
    schema = "naris.p0.hero-runtime-qa.v1"
    status = if ($RuntimeGate -and $ScreenshotPresent) { "PASS_EVIDENCE_READY" } else { "FAIL_GATE" }
    project = "CALL OF NARIS"
    master_project = $UProject
    qa_map = $QaMap
    scene_prepared = $true
    screenshot_present = $ScreenshotPresent
    screenshot_path = if ($ScreenshotPresent) { $ScreenshotOut } else { $null }
    combat_exit_code = $CombatExit
    combat_pass = $CombatPass
    fatal_findings = @($FatalFindings)
    technical_runtime_gate = $RuntimeGate
    visual_acceptance = $false
    visual_review_required = $true
    replacement_allowed = $false
    next_gate = "Inspect P0-04B_HeroCompare.png; if approved, create P0-04B visual decision then run P0-05 promotion."
}

$Result | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $FinalReport -Encoding UTF8
Write-Host ($Result | ConvertTo-Json -Depth 7)

if (-not $RuntimeGate) {
    throw "P0-04B runtime combat/fatal gate failed."
}
if (-not $ScreenshotPresent) {
    throw "P0-04B screenshot gate failed."
}

Write-Host "[P0-04B] PASS_EVIDENCE_READY"
Write-Host "[P0-04B] Screenshot: $ScreenshotOut"
Write-Host "[P0-04B] Promotion remains blocked pending visual review."