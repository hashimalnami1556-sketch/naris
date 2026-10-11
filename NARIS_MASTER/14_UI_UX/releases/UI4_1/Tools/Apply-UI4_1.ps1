param(
    [string]$ProjectRoot = 'C:\Users\Admin\NARIS',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.7',
    [ValidateRange(0,180)][int]$LogWaitSeconds = 45
)
$ErrorActionPreference = 'Stop'

$uproject = Join-Path $ProjectRoot 'NARIS.uproject'
$hudH = Join-Path $ProjectRoot 'Source\NarisCore\Public\NarisHUD.h'
$hudC = Join-Path $ProjectRoot 'Source\NarisCore\Private\NarisHUD.cpp'
$gmC = Join-Path $ProjectRoot 'Source\NarisCore\Private\NarisGameModeBase.cpp'
$input = Join-Path $ProjectRoot 'Config\DefaultInput.ini'
$ubt = Join-Path $EngineRoot 'Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe'
$uat = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$validator = Join-Path $PSScriptRoot 'Validate-UI4_1.ps1'

# Preflight before writing any project file. A failed preflight leaves the project untouched.
foreach ($f in @($uproject, $hudH, $hudC, $gmC, $input, $ubt, $uat, $validator)) {
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) {
        throw "Required file missing: $f"
    }
}
$gm = Get-Content -LiteralPath $gmC -Raw
if ($gm -notmatch 'NarisDirectPlay') {
    throw 'Explicit DirectPlay flag marker missing. Refusing unsafe patch.'
}
if ($gm -match 'bSmoke\|\|!bFrontEnd') {
    throw 'Direct-play regression detected in GameMode.'
}
$hc = Get-Content -LiteralPath $hudC -Raw
foreach ($marker in @('StartGame', 'ContinueGame', 'OpenSettings', 'ExitGame', 'NARSIC')) {
    if ($hc -notmatch [regex]::Escape($marker)) {
        throw "HUD marker missing: $marker"
    }
}
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) {
    throw 'Unreal Editor is running. Save your work and close it manually before packaging; no process will be killed automatically.'
}
$out = Join-Path $ProjectRoot 'Builds\WindowsDevelopment_UI4_1'
if (Test-Path -LiteralPath $out) {
    throw "Target build directory already exists. Preserve or move it before retrying: $out"
}

# Back up the exact source files that this workflow may affect.
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backup = Join-Path $ProjectRoot "Backups\UI4_1\$stamp"
New-Item -ItemType Directory -Force -Path $backup | Out-Null
Copy-Item -LiteralPath $hudH -Destination (Join-Path $backup 'NarisHUD.h')
Copy-Item -LiteralPath $hudC -Destination (Join-Path $backup 'NarisHUD.cpp')
Copy-Item -LiteralPath $gmC -Destination (Join-Path $backup 'NarisGameModeBase.cpp')
Copy-Item -LiteralPath $input -Destination (Join-Path $backup 'DefaultInput.ini')

$ini = Get-Content -LiteralPath $input -Raw
if ($ini -notmatch '(?m)^\+ActionMappings=\(ActionName="Resonance"[^\r\n]*Key=R\)') {
    $mapping = '+ActionMappings=(ActionName="Resonance",bShift=False,bCtrl=False,bAlt=False,bCmd=False,Key=R)'
    $ini = $ini.TrimEnd() + [Environment]::NewLine + $mapping + [Environment]::NewLine
    [System.IO.File]::WriteAllText($input, $ini, [System.Text.UTF8Encoding]::new($false))
}

& $ubt NARISEditor Win64 Development "-Project=$uproject" -NoHotReloadFromIDE
if ($LASTEXITCODE -ne 0) { throw "NARISEditor build failed: $LASTEXITCODE" }

New-Item -ItemType Directory -Force -Path $out | Out-Null
$uatArgs = @('BuildCookRun', "-project=$uproject", '-noP4', '-platform=Win64',
    '-clientconfig=Development', '-build', '-cook', '-stage', '-pak', '-package',
    '-archive', "-archivedirectory=$out", '-utf8output')
& $uat @uatArgs
if ($LASTEXITCODE -ne 0) { throw "Packaging failed: $LASTEXITCODE" }

# BuildCookRun often archives as Windows\NARIS.exe, not $out\NARIS.exe.
$gameExe = Get-ChildItem -LiteralPath $out -Filter 'NARIS.exe' -File -Recurse -ErrorAction SilentlyContinue |
    Sort-Object FullName | Select-Object -First 1
if (-not $gameExe) { throw "Packaged NARIS.exe not found recursively under $out" }

$launchUtc = [DateTime]::UtcNow
$process = Start-Process -FilePath $gameExe.FullName -WorkingDirectory $gameExe.DirectoryName -ArgumentList @(
    '-windowed', '-ResX=1280', '-ResY=720', '-log'
) -PassThru
Start-Sleep -Seconds 8
$process.Refresh()
if ($process.HasExited) {
    # A packaged root executable may launch a Win64-Development child and exit.
    $children = @(Get-Process -Name @('NARIS-Win64-Development', 'NARIS-Win64-Shipping', 'NARIS') -ErrorAction SilentlyContinue |
        Where-Object { try { $_.StartTime.ToUniversalTime() -ge $launchUtc.AddSeconds(-3) } catch { $false } })
    if ($children.Count -eq 0) {
        throw "Packaged NARIS exited (code $($process.ExitCode)) and no new runtime process was found. Check fresh logs."
    }
}
& $validator -ProjectRoot $ProjectRoot -BuildName 'WindowsDevelopment_UI4_1' -LaunchedAtUtc $launchUtc -WaitSeconds $LogWaitSeconds
if ($LASTEXITCODE -ne 0) { throw "Packaged runtime log validation failed: $LASTEXITCODE" }
Write-Host '[NARIS] Packaged process launched and fresh runtime markers validated. Visual/click-through QA is still required.'
