[CmdletBinding()]
param(
    [string]$EngineRoot = "C:\Program Files\Epic Games\UE_5.7",
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [switch]$Apply,
    [string]$TemplateMap
)
$ErrorActionPreference = "Stop"
$ProjectRoot = Join-Path $RepoRoot "unreal\NARIS_W04"
$Project = Join-Path $ProjectRoot "NARIS_W04.uproject"
$Editor = Join-Path $EngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$VersionPath = Join-Path $EngineRoot "Engine\Build\Build.version"
$Entry = Join-Path $ProjectRoot "Content\Python\naris_stage29_batch.py"
foreach ($Path in @($Project, $Editor, $VersionPath, $Entry)) {
    if (!(Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Required file missing: $Path" }
}
$Descriptor = Get-Content -LiteralPath $Project -Raw | ConvertFrom-Json
$Version = Get-Content -LiteralPath $VersionPath -Raw | ConvertFrom-Json
$EngineBaseline = "$($Version.MajorVersion).$($Version.MinorVersion)"
if ($Descriptor.EngineAssociation -ne $EngineBaseline) { throw "Engine $EngineBaseline does not match project baseline $($Descriptor.EngineAssociation)" }
if ($Apply -and (!$TemplateMap -or $TemplateMap -notmatch '^/Game/[A-Za-z0-9_/]+$')) {
    throw "Apply requires an existing ground-bearing /Game/... TemplateMap"
}
$InvocationId = [Guid]::NewGuid().ToString("N")
$InvocationDir = Join-Path $ProjectRoot "Saved\TestReports\Stage29Invocation_$InvocationId"
if (Test-Path -LiteralPath $InvocationDir) { throw "Invocation directory already exists" }
New-Item -ItemType Directory -Path $InvocationDir | Out-Null
$Receipt = Join-Path $InvocationDir "receipt.json"
$Log = Join-Path $InvocationDir "UnrealEditor.log"
$Names = @("NARIS_STAGE29_RECEIPT", "NARIS_STAGE29_MODE", "NARIS_STAGE29_TEMPLATE")
$Prior = @{}
foreach ($Name in $Names) { $Prior[$Name] = [Environment]::GetEnvironmentVariable($Name, "Process") }
try {
    $env:NARIS_STAGE29_RECEIPT = $Receipt
    $env:NARIS_STAGE29_MODE = if ($Apply) { "apply" } else { "dry_run" }
    $env:NARIS_STAGE29_TEMPLATE = $TemplateMap
    Write-Host "[Stage29] $($env:NARIS_STAGE29_MODE) | reports: $InvocationDir"
    & $Editor $Project "-ExecutePythonScript=$Entry" "-abslog=$Log" -unattended -nop4 -nosplash -NullRHI
    if ($LASTEXITCODE -ne 0) { throw "Unreal exited with $LASTEXITCODE; retain $InvocationDir" }
    if (!(Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw "No current invocation receipt; retain $InvocationDir" }
    $Result = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    $ExpectedMode = if ($Apply) { "apply" } else { "dry_run" }
    $ExpectedStatus = if ($Apply) { "authoring_complete_requires_PIE" } else { "preflight_complete_requires_apply" }
    if ($Result.schema -ne "naris.stage29.invocation.v1" -or $Result.mode -ne $ExpectedMode -or $Result.status -ne $ExpectedStatus -or @($Result.errors).Count -ne 0) {
        throw "Stage29 invocation failed validation; retain $InvocationDir"
    }
    if ($Result.run_id -notmatch '^[a-f0-9]{32}$') { throw "Missing/invalid engine report run ID" }
    $EngineReport = Join-Path $ProjectRoot "Saved\TestReports\stage29_g1_$($Result.run_id).json"
    if (!(Test-Path -LiteralPath $EngineReport -PathType Leaf)) { throw "Receipt has no corresponding engine report" }
    $Measured = Get-Content -LiteralPath $EngineReport -Raw | ConvertFrom-Json
    if ($Measured.run_id -ne $Result.run_id -or $Measured.mode -ne $ExpectedMode -or @($Measured.errors).Count -ne 0) {
        throw "Receipt and engine report disagree"
    }
    if ($Apply -and ($Measured.map_saved -ne $true -or $Measured.placed -ne 136 -or $Measured.attempted -ne 136)) {
        throw "Expected 136 measured/saved placements; inspect $EngineReport"
    }
    Copy-Item -LiteralPath $EngineReport -Destination (Join-Path $InvocationDir "engine-report.json")
    Get-FileHash -LiteralPath $Receipt, (Join-Path $InvocationDir "engine-report.json") -Algorithm SHA256 |
        Select-Object Path, Hash | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $InvocationDir "checksums.json") -Encoding UTF8
    Write-Host "Stage29 invocation complete. G1 requires PIE/material/streaming/traversal review. G2 and G3 NOT RUN."
} finally {
    foreach ($Name in $Names) { [Environment]::SetEnvironmentVariable($Name, $Prior[$Name], "Process") }
}
