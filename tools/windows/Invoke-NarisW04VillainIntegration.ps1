param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT
)
$ErrorActionPreference = "Stop"
if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "Set UNREAL_ENGINE_ROOT to the installed Unreal Engine 5.7 directory."
}
$Project = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$Build = Join-Path $UnrealEngineRoot "Engine\Build\BatchFiles\Build.bat"
$Editor = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$Blockout = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_author_w04_production_blockout.py"
$Villains = Join-Path $RepoRoot "unreal\NARIS_W04\Content\Python\naris_author_w04_villains.py"
$Roster = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Data\W04_VillainEncounterRoster.json"
foreach ($Path in @($Project, $Build, $Editor, $Blockout, $Villains, $Roster)) {
    if (-not (Test-Path $Path)) { throw "Missing required path: $Path" }
}
$Descriptor = Get-Content -Raw $Project | ConvertFrom-Json
if ($Descriptor.EngineAssociation -ne "5.7") {
    throw "W04 is not configured for Unreal Engine 5.7. Stop before authoring."
}
Write-Host "[NARIS] Build W04 Unreal editor"
& $Build "NARIS_W04Editor" "Win64" "Development" $Project "-WaitMutex"
if ($LASTEXITCODE -ne 0) { throw "Editor build failed ($LASTEXITCODE)" }

foreach ($Entry in @(@("Base W04 development map", $Blockout),
                     @("Interactive villain encounters and navigation volumes", $Villains))) {
    Write-Host "[NARIS] Authoring: $($Entry[0])"
    & $Editor $Project "-ExecutePythonScript=$($Entry[1])" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
    if ($LASTEXITCODE -ne 0) { throw "Authoring failed at $($Entry[0]) ($LASTEXITCODE)" }
}
$MapFile = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Maps\W04_AshenForest_Blockout.umap"
if (-not (Test-Path $MapFile)) { throw "Development map missing after authoring: $MapFile" }
Write-Host "[NARIS] Development encounters authored. Open blockout in Unreal Editor."
Write-Host "[NARIS] Build navigation, verify pathfinding with P, and run PIE."
Write-Host "[NARIS] No production assets or Shipping release were approved by this script."
