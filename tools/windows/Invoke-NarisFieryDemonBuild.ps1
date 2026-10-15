<#
.SYNOPSIS
    NARIS W04: rigged Fiery Demon GLB -> Blender FBX -> UE5.7 QA map -> optional Windows build/run.
.DESCRIPTION
    QA-first. Does not silently modify the existing Ash Gate or shipping map.
    Launch smoke checks the process and a NEW map-load log, not combat/gameplay quality.
.EXAMPLE
    .\tools\windows\Invoke-NarisFieryDemonBuild.ps1 `
      -DemonGlb 'C:\NARIS\Assets\NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb' `
      -EnvironmentGlb 'C:\NARIS\Assets\Environmental 1.glb' -Package -Launch
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [Parameter(Mandatory = $true)][string]$DemonGlb,
    [string]$EnvironmentGlb = "",
    [string]$BlenderExe = "",
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT,
    [string]$TargetMap = "/Game/NARIS/W04/Maps/L_FieryDemon_QA",
    [switch]$AllowProductionMapEdit,
    [switch]$Package,
    [switch]$Launch,
    [switch]$SmokeOnly,
    [int]$LaunchSmokeSeconds = 20
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Assert-File([string]$Path, [string]$Description) {
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing $Description at: $Path"
    }
}
function Assert-Exit([string]$Stage) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Stage exited with code $LASTEXITCODE"
    }
}
function Write-Json([string]$Path, $Value) {
    $Value | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding utf8
}

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

if ($Launch -and -not $Package) {
    throw "Launch requires -Package; refuse to run a stale EXE"
}
if ($SmokeOnly -and -not $Launch) {
    throw "SmokeOnly requires -Launch"
}
if ($LaunchSmokeSeconds -lt 5 -or $LaunchSmokeSeconds -gt 180) {
    throw "LaunchSmokeSeconds must be between 5 and 180"
}
if ($TargetMap -ne "/Game/NARIS/W04/Maps/L_FieryDemon_QA" -and -not $AllowProductionMapEdit) {
    throw "Production map edit requires -AllowProductionMapEdit"
}
if ($TargetMap -notmatch '^/Game/[A-Za-z0-9_/-]+$') {
    throw "Invalid Unreal map object path"
}
if (-not $UnrealEngineRoot) {
    $UnrealEngineRoot = "C:\Program Files\Epic Games\UE_5.7"
}
if (-not $BlenderExe) {
    $resolvedBlender = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($resolvedBlender) {
        $BlenderExe = $resolvedBlender.Source
    } else {
        $blenderOptions = @(Get-ChildItem "C:\Program Files\Blender Foundation" -Filter blender.exe -File -Recurse -ErrorAction SilentlyContinue)
        if ($blenderOptions.Count -gt 0) {
            $BlenderExe = ($blenderOptions | Sort-Object FullName -Descending | Select-Object -First 1).FullName
        }
    }
}

$Project = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Build = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\Build.bat"
$Editor = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$Uat = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\RunUAT.bat"
$BlenderScript = Join-Path $RepoRoot "tools\blender\export_naris_fiery_demon.py"
$Importer = Join-Path $RepoRoot "tools\unreal\import_fiery_demon_runtime.py"
foreach ($item in @($Project, $Build, $Editor, $Uat, $BlenderScript, $Importer)) {
    Assert-File $item "required dependency"
}
Assert-File $BlenderExe "Blender executable"
Assert-File $DemonGlb "animated Fiery Demon GLB"
if ($EnvironmentGlb) { Assert-File $EnvironmentGlb "environment GLB" }

# Prevent saving actor data while another Unreal Editor has the same project open.
$runningEditors = @(Get-Process -Name UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue)
if ($runningEditors.Count -gt 0) {
    throw "Close running UnrealEditor/UnrealEditor-Cmd processes before writing the QA map."
}

$ReportsRoot = Join-Path $RepoRoot "artifacts\fiery_demon_qa"
$PrepDir = Join-Path $ReportsRoot "intermediate"
$ArchiveDir = Join-Path $ReportsRoot ("WindowsDevelopment_" + [DateTime]::UtcNow.ToString("yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Path $PrepDir -Force | Out-Null

$DemonFbx = Join-Path $PrepDir "NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.fbx"
$BlenderReport = Join-Path $PrepDir "naris_fiery_demon_blender.json"
$EnvFbx = Join-Path $PrepDir "NARIS_AshGate_Environment.fbx"
$EnvReport = Join-Path $PrepDir "naris_ash_gate_blender.json"
$ImportReport = Join-Path $ReportsRoot "naris_fiery_demon_editor_import.json"
$BuildReport = Join-Path $ReportsRoot "naris_fiery_demon_build_report.json"

Write-Host "[NARIS] 1/6 Exporting Fiery Demon FBX (skinned and animated)"
& $BlenderExe -b -P $BlenderScript -- --input $DemonGlb --output $DemonFbx --report $BlenderReport --min-actions 4
Assert-Exit "Fiery Demon Blender export"
Assert-File $DemonFbx "skeletal FBX"
Assert-File $BlenderReport "Blender provenance report"
$blenderData = Get-Content -LiteralPath $BlenderReport -Raw | ConvertFrom-Json
if ($blenderData.status -ne "fbx_exported_unreal_import_unverified" -or
    [int]$blenderData.skinned_bones -lt 15 -or [int]$blenderData.action_count -lt 4) {
    throw "Animation/rig Blender gate failed"
}

if ($EnvironmentGlb) {
    Write-Host "[NARIS] 2/6 Exporting separate static Ash Gate environment"
    & $BlenderExe -b -P $BlenderScript -- --input $EnvironmentGlb --output $EnvFbx --report $EnvReport --static
    Assert-Exit "Ash Gate Blender export"
    Assert-File $EnvFbx "static environment FBX"
}

Write-Host "[NARIS] 3/6 Compiling native NARIS_W04Editor Win64 Development"
& $Build NARIS_W04Editor Win64 Development $Project -WaitMutex
Assert-Exit "Native Unreal C++ editor build"

$env:NARIS_DEMON_FBX = $DemonFbx
$env:NARIS_REPORT_JSON = $ImportReport
$env:NARIS_TARGET_MAP = $TargetMap
$env:NARIS_ALLOW_MAP_EDIT = if ($AllowProductionMapEdit) { "1" } else { "0" }
$env:NARIS_ENV_FBX = if ($EnvironmentGlb) { $EnvFbx } else { "" }
try {
    if (Test-Path -LiteralPath $ImportReport) { Remove-Item -LiteralPath $ImportReport -Force }
    Write-Host "[NARIS] 4/6 Importing skeletal boss, animations and map actors into Unreal Editor"
    & $Editor $Project "-ExecutePythonScript=$Importer" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
    Assert-Exit "Fiery Demon Unreal asset import"
} finally {
    Remove-Item Env:NARIS_DEMON_FBX,Env:NARIS_REPORT_JSON,Env:NARIS_TARGET_MAP,Env:NARIS_ALLOW_MAP_EDIT,Env:NARIS_ENV_FBX -ErrorAction SilentlyContinue
}
Assert-File $ImportReport "Unreal Editor import report"
$importData = Get-Content -LiteralPath $ImportReport -Raw | ConvertFrom-Json
if ($importData.status -ne "editor_map_saved" -or
    $importData.map -ne $TargetMap -or
    [int]$importData.animations_imported -lt 3 -or
    $importData.pie_tested -ne $false) {
    throw "Unreal map/animation authoring acceptance failed"
}
$mapRelative = $TargetMap.Substring(6).Replace("/", "\")
$mapFile = Join-Path (Join-Path $RepoRoot "unreal\NARIS_W04\Content") ($mapRelative + ".umap")
Assert-File $mapFile "L_FieryDemon_QA.umap (actual editor-created level)"

$report = [ordered]@{
    status = "editor_map_saved"
    native_editor_compile = "pass"
    blender_export = "pass"
    unreal_import = "pass"
    map = $TargetMap
    animation_count = [int]$importData.animations_imported
    package_status = "not_requested"
    launch_status = "not_requested"
    interactive_pie_tested = $false
    combat_playtested = $false
    shipping_approved = $false
}
Write-Json $BuildReport $report

if ($Package) {
    if ($TargetMap -ne "/Game/NARIS/W04/Maps/L_FieryDemon_QA") {
        throw "Windows QA packaging is restricted to isolated Fiery Demon QA level"
    }
    # Regenerate English/Arabic localization resources after adding HUDFieryDemon.
    $LocalizationScript = Join-Path $RepoRoot "tools\windows\Invoke-NarisLocalization.ps1"
    Assert-File $LocalizationScript "localization cook script"
    Write-Host "[NARIS] Gathering/compiling EN+AR localization before cook"
    & $LocalizationScript -RepoRoot $RepoRoot -UnrealEngineRoot $UnrealEngineRoot
    Assert-Exit "Unreal localization gather/compile"
    Write-Host "[NARIS] 5/6 BuildCookRun: cooking Fiery Demon QA map for Windows"
    $uatArgs = @(
        "BuildCookRun", "-project=$Project", "-noP4", "-platform=Win64",
        "-clientconfig=Development", "-build", "-cook",
        "-map=L_FieryDemon_QA", "-stage", "-pak", "-package", "-archive",
        "-archivedirectory=$ArchiveDir", "-utf8output"
    )
    & $Uat @uatArgs
    Assert-Exit "Fiery Demon BuildCookRun"
    $candidateExe = @(Get-ChildItem -LiteralPath $ArchiveDir -Filter "NARIS_W04.exe" -Recurse -File -ErrorAction SilentlyContinue)
    if ($candidateExe.Count -eq 0) { throw "No NARIS_W04.exe in fresh QA build" }
    $exe = $candidateExe | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    $report.package_status = "buildcookrun_pass"
    $report["package_exe"] = $exe.FullName
    Write-Json $BuildReport $report

    if ($Launch) {
        Write-Host "[NARIS] 6/6 Launching packaged QA map (not interactive gameplay QA)"
        $launchedAt = [DateTime]::UtcNow
        # URL map override: default W04_Prototype must not silently hide the demon QA level.
        $process = Start-Process -FilePath $exe.FullName -ArgumentList @(
            "/Game/NARIS/W04/Maps/L_FieryDemon_QA", "-windowed",
            "-ResX=1280", "-ResY=720", "-log", "-nosplash"
        ) -PassThru
        if ($process.WaitForExit($LaunchSmokeSeconds * 1000)) {
            throw "Packaged QA game exited early with code $($process.ExitCode)"
        }
        $smokeAccepted = $false
        try {
            $roots = @($ArchiveDir, (Join-Path $env:LOCALAPPDATA "NARIS_W04\Saved\Logs"))
            $fresh = foreach ($directory in $roots) {
                if (Test-Path -LiteralPath $directory) {
                    Get-ChildItem -LiteralPath $directory -Filter "*.log" -Recurse -File -ErrorAction SilentlyContinue |
                        Where-Object { $_.LastWriteTimeUtc -ge $launchedAt.AddSeconds(-3) }
                }
            }
            # Map paths appear in launch arguments too; only a real Unreal
            # LogLoad: LoadMap event proves that the intended level was opened.
            $expectedMapLogRegex = 'LogLoad:\s*LoadMap:\s*/Game/NARIS/W04/Maps/L_FieryDemon_QA(?![A-Za-z0-9_])'
            # The READY marker is emitted by ANarisFieryDemonBoss::BeginPlay only
            # when its SkeletalMesh and three required AnimSequences are bound.
            $expectedBossLogRegex = 'LogTemp:\s*(?:Display:\s*)?NARIS_FIERY_DEMON_RUNTIME_READY(?![A-Za-z0-9_])'
            $mapLoadFound = $false
            $bossReadyFound = $false
            foreach ($log in @($fresh)) {
                $text = Get-Content -LiteralPath $log.FullName -Raw -ErrorAction SilentlyContinue
                if ($text -match $expectedMapLogRegex) {
                    $mapLoadFound = $true
                    if ($text -match $expectedBossLogRegex) {
                        $bossReadyFound = $true
                        break
                    }
                }
            }
            if (-not $mapLoadFound) {
                throw "No FRESH Unreal LogLoad: LoadMap event for L_FieryDemon_QA in packaged log"
            }
            if (-not $bossReadyFound) {
                throw "Fiery Demon actor/mesh/animation readiness marker missing from packaged runtime log"
            }
            $report.launch_status = "process_alive_map_loaded_and_demon_actor_ready"
            $report["process_id"] = $process.Id
            Write-Json $BuildReport $report
            $smokeAccepted = $true
        } finally {
            if ($SmokeOnly -or -not $smokeAccepted) {
                if (-not $process.HasExited) {
                    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                }
            }
        }
        if ($smokeAccepted -and -not $SmokeOnly) {
            Write-Host "[NARIS] Game remains running. PID: $($process.Id)"
        }
    }
}
Write-Host "[NARIS] Fiery Demon QA staged: $BuildReport"
Write-Host "[NARIS] PIE combat verification, 60 FPS benchmark and Shipping remain NOT APPROVED"
