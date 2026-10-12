param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [Parameter(Mandatory=$true)][string]$PrototypePackage,
    [string]$BlenderExecutable = $env:BLENDER_EXE,
    [string]$UnrealEngineRoot = $env:UNREAL_ENGINE_ROOT
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path $PrototypePackage -PathType Leaf)) {
    throw "Villain GLB prototype package missing: $PrototypePackage"
}
if (-not $BlenderExecutable -or -not (Test-Path $BlenderExecutable)) {
    throw "BlenderExecutable must be an installed Blender executable."
}
if (-not $UnrealEngineRoot -or -not (Test-Path $UnrealEngineRoot)) {
    throw "UnrealEngineRoot must be an installed Unreal Engine 5.7 location."
}
$Project = Join-Path $RepoRoot 'unreal\NARIS_W04\NARIS_W04.uproject'
$Editor = Join-Path $UnrealEngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$ImportScript = Join-Path $RepoRoot 'unreal\NARIS_W04\Content\Python\naris_import_villain_fbx.py'
$Bootstrap = Join-Path $RepoRoot 'tools\windows\Invoke-NarisW04VillainIntegration.ps1'
$Stage = Join-Path $RepoRoot 'unreal\NARIS_W04\Saved\NarisVillainPrototypeIntake'
foreach ($Path in @($Project, $Editor, $ImportScript, $Bootstrap)) {
    if (-not (Test-Path $Path)) { throw "Missing required file: $Path" }
}
New-Item -ItemType Directory -Force -Path $Stage | Out-Null
Expand-Archive -LiteralPath $PrototypePackage -DestinationPath $Stage -Force
$InputModels = Join-Path $Stage 'models'
$Converter = Join-Path $Stage 'convert_glb_to_fbx_blender.py'
$ExportedFBX = Join-Path $Stage 'fbx'
if (-not (Test-Path $Converter) -or -not (Test-Path $InputModels)) {
    throw 'Archive must contain models/ and convert_glb_to_fbx_blender.py'
}
Write-Host '[NARIS] Convert GLB prototype rigs and clips with Blender'
& $BlenderExecutable -b -P $Converter -- $InputModels $ExportedFBX
if ($LASTEXITCODE -ne 0) { throw "Blender FBX conversion failed ($LASTEXITCODE)" }
if ((Get-ChildItem -Path $ExportedFBX -Filter 'SK_*.fbx' -File).Count -ne 7) {
    throw 'Expected 7 exported FBX files.'
}
Write-Host '[NARIS] Build editor and author W04 development encounters'
& $Bootstrap -RepoRoot $RepoRoot -UnrealEngineRoot $UnrealEngineRoot
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Villain authoring failed ($LASTEXITCODE)" }
$env:NARIS_VILLAIN_FBX_DIR = $ExportedFBX
Write-Host '[NARIS] Import SkeletalMesh and animation clips, then bind W04 actors'
& $Editor $Project "-ExecutePythonScript=$ImportScript" -unattended -nop4 -nosplash -stdout -FullStdOutLogOutput
if ($LASTEXITCODE -ne 0) { throw "Villain FBX import validation failed ($LASTEXITCODE)" }
Write-Host '[NARIS] Intake complete for developmental testing only. Run Unreal PIE and profile before approval.'
