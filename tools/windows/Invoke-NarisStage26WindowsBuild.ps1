param(
  [Parameter(Mandatory=$true)][string]$RepoRoot,
  [Parameter(Mandatory=$true)][string]$UnrealEngineRoot,
  [string]$ArchiveDir = ""
)
$ErrorActionPreference = "Stop"
$rc = Join-Path $RepoRoot "tools\windows\Invoke-NarisWindowsReleaseCandidate.ps1"
$uproject = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$mapAsset = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Maps\W04_AshenForest.umap"
$editor = Join-Path $UnrealEngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
foreach($path in @($rc,$uproject,$mapAsset,$editor)) {
  if (-not (Test-Path -LiteralPath $path)) { throw "Release build prerequisite missing: $path" }
}
Write-Host "[NARIS Stage26] Running canonical strict W04 Windows RC validation and BuildCookRun"
$args = @{RepoRoot=$RepoRoot; UnrealEngineRoot=$UnrealEngineRoot}
if ($ArchiveDir) {$args.ArchiveDir=$ArchiveDir}
& $rc @args
if (-not $?) {throw "Canonical release candidate pipeline failed"}
Write-Host "[NARIS Stage26] Validate RC report, EXE, logs and runtime before promotion"
