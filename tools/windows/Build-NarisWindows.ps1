param(
  [string]$EngineRoot = $env:UNREAL_ENGINE_ROOT,
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
  [ValidateSet("Development","Shipping")][string]$Configuration = "Shipping"
)
$ErrorActionPreference = "Stop"
if (-not $EngineRoot) { $EngineRoot = "C:\Program Files\Epic Games\UE_5.7" }
$Project = Join-Path $RepoRoot "unreal\NARIS_W04\NARIS_W04.uproject"
$VersionFile = Join-Path $EngineRoot "Engine\Build\Build.version"
foreach ($Required in @($Project, $VersionFile)) {
  if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) { throw "Required file missing: $Required" }
}
$Version = Get-Content -LiteralPath $VersionFile -Raw | ConvertFrom-Json
if ($Version.MajorVersion -ne 5 -or $Version.MinorVersion -ne 7) { throw "The canonical W04 project requires Unreal Engine 5.7" }
$Descriptor = Get-Content -LiteralPath $Project -Raw | ConvertFrom-Json
if ($Descriptor.EngineAssociation -ne "5.7") { throw "Project engine association does not match UE 5.7" }
# A unique archive prevents an earlier executable from satisfying this invocation.
$RunId = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ") + "_" + [Guid]::NewGuid().ToString("N")
$Archive = Join-Path $RepoRoot ("Builds\Windows_" + $Configuration + "\" + $RunId)
if ($Configuration -eq "Shipping") {
  $MapFile = Join-Path $RepoRoot "unreal\NARIS_W04\Content\NARIS\W04\Maps\W04_AshenForest.umap"
  if (-not (Test-Path -LiteralPath $MapFile -PathType Leaf)) {
    throw "FINAL MAP GATE FAILED: W04_AshenForest.umap must be authored, validated and saved before Shipping"
  }
  $Gate = Join-Path $PSScriptRoot "Invoke-NarisWindowsReleaseCandidate.ps1"
} else {
  $Gate = Join-Path $PSScriptRoot "Invoke-NarisWindowsPackage.ps1"
}
if (-not (Test-Path -LiteralPath $Gate)) { throw "Canonical package gate missing: $Gate" }
& $Gate -RepoRoot $RepoRoot -UnrealEngineRoot $EngineRoot -ArchiveDir $Archive
if (-not $?) { throw "Canonical Windows package gate failed" }
$Executable = Get-ChildItem -LiteralPath $Archive -Filter "NARIS_W04.exe" -Recurse -File | Select-Object -First 1
if (-not $Executable -or $Executable.Length -le 0) { throw "No non-empty executable was generated in this run" }
$Hash = (Get-FileHash -LiteralPath $Executable.FullName -Algorithm SHA256).Hash
$Report = [ordered]@{
  schema = "naris.windows.package-invocation.v1"
  status = "package_generated"
  configuration = $Configuration
  run_id = $RunId
  archive = $Archive
  executable = $Executable.FullName
  executable_sha256 = $Hash
  release_approved = $false
  note = "Package creation is separate from packaged gameplay, performance and clean-machine acceptance."
}
$Report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Archive "naris_package_invocation.json") -Encoding UTF8
Write-Host "[NARIS] Windows package generated: $($Executable.FullName)"
Write-Host "[NARIS] SHA256: $Hash"
