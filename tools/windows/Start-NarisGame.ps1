# Safely discover and launch the most recent NARIS / NARSIC Windows package.
# This script does NOT rebuild, overwrite game saves, or terminate Unreal Editor.
[CmdletBinding()]
param(
    [string]$ProjectRoot = 'C:\Users\Admin\NARIS_CANON',
    [string]$RepoRoot = '',
    [string]$Executable = '',
    [ValidateRange(0, 120)][int]$CheckAfterSeconds = 8,
    [switch]$ListOnly
)
$ErrorActionPreference = 'Stop'

$names = @(
    'NARIS.exe', 'NARIS_W04.exe', 'NARSIC.exe',
    'NARIS-Win64-Shipping.exe', 'NARIS-Win64-Development.exe',
    'NARIS_W04-Win64-Shipping.exe', 'NARIS_W04-Win64-Development.exe',
    'NARSIC-Win64-Shipping.exe', 'NARSIC-Win64-Development.exe'
)
$roots = @(
    (Join-Path $ProjectRoot 'Builds'),
    (Join-Path $ProjectRoot 'Saved\StagedBuilds'),
    (Join-Path $ProjectRoot 'artifacts\windows'),
    (Join-Path $ProjectRoot 'unreal\NARIS_W04\Saved\StagedBuilds')
)
# Also search packages next to the checked-in launcher when copied checkouts differ.
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    $roots += (Join-Path $RepoRoot 'artifacts\windows')
    $roots += (Join-Path $RepoRoot 'unreal\NARIS_W04\Saved\StagedBuilds')
}
$roots = @($roots | Select-Object -Unique | Where-Object { Test-Path -LiteralPath $_ -PathType Container })

$candidates = @()
if (-not [string]::IsNullOrWhiteSpace($Executable)) {
    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
        throw "Explicit game executable not found: $Executable"
    }
    if ([System.IO.Path]::GetFileName($Executable) -notin $names) {
        throw "Unsupported executable name. Expected one of: $($names -join ', ')"
    }
    $candidates = @(Get-Item -LiteralPath $Executable)
} else {
    foreach ($root in $roots) {
        $candidates += @(
            Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.exe' -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -in $names }
        )
    }
}

$candidates = @($candidates | Sort-Object -Property FullName -Unique |
    Sort-Object -Property LastWriteTimeUtc -Descending)
if ($candidates.Count -eq 0) {
    throw @"
No packaged NARIS executable found.
Searched: $($roots -join '; ')
Expected: $($names -join ', ').
Build/package in Unreal first; an .uproject is not a playable executable.
"@
}

Write-Host '[NARIS] Available packaged executables:'
$candidates | Select-Object -First 10 FullName, LastWriteTime, Length |
    Format-Table -AutoSize | Out-Host
if ($ListOnly) { return }

$game = $candidates[0]
$startedAtUtc = [DateTime]::UtcNow
Write-Host "[NARIS] Launching: $($game.FullName)"
$process = Start-Process -FilePath $game.FullName -WorkingDirectory $game.DirectoryName -ArgumentList @(
    '-windowed', '-ResX=1280', '-ResY=720', '-log'
) -PassThru

if ($CheckAfterSeconds -gt 0) { Start-Sleep -Seconds $CheckAfterSeconds }
$process.Refresh()
# Unreal packaged roots may be a short-lived bootstrap that starts a Win64 game child.
$activeGame = $null
if ($process.HasExited) {
    $packagePrefix = $game.DirectoryName.TrimEnd('\') + '\'
    $children = @(Get-CimInstance Win32_Process -Filter "ParentProcessId = $($process.Id)" |
        Where-Object {
            $_.Name -in $names -and $_.ExecutablePath -and
            $_.ExecutablePath.StartsWith($packagePrefix, [StringComparison]::OrdinalIgnoreCase)
        })
    $activeGame = @(
        foreach ($child in $children) {
            Get-Process -Id $child.ProcessId -ErrorAction SilentlyContinue | Where-Object {
                try { $_.StartTime.ToUniversalTime() -ge $startedAtUtc } catch { $false }
            }
        }
    )
    if ($activeGame.Count -eq 0) {
        throw "NARIS exited during startup (exit code $($process.ExitCode)); no owned game child in this package was found. Inspect Saved\Logs / CrashReportClient logs."
    }
    Write-Host '[NARIS] Package bootstrap exited, but a newly started game process is running.'
}

$logRoots = @(
    (Join-Path $ProjectRoot 'Saved\Logs'),
    (Join-Path $game.DirectoryName 'Saved\Logs'),
    (Join-Path $game.DirectoryName 'NARIS\Saved\Logs'),
    (Join-Path $game.DirectoryName 'NARIS_W04\Saved\Logs')
)
if ($env:LOCALAPPDATA) {
    foreach ($app in @('NARIS', 'NARIS_W04', 'NARSIC', 'UnrealGame')) {
        $logRoots += (Join-Path $env:LOCALAPPDATA "$app\Saved\Logs")
    }
}
$recentLogs = @(
    foreach ($root in ($logRoots | Select-Object -Unique)) {
        if (Test-Path -LiteralPath $root -PathType Container) {
            Get-ChildItem -LiteralPath $root -Filter '*.log' -File -ErrorAction SilentlyContinue |
                Where-Object { $_.LastWriteTimeUtc -ge $startedAtUtc.AddSeconds(-2) }
        }
    }
)
$recentLogs = @($recentLogs | Sort-Object LastWriteTimeUtc -Descending)
if ($recentLogs.Count -gt 0) {
    $logFile = $recentLogs[0]
    $fatal = @(Select-String -LiteralPath $logFile.FullName -Pattern @(
        'Fatal error:', 'Unhandled Exception', 'Assertion failed:', 'LowLevelFatalError'
    ) -SimpleMatch -ErrorAction SilentlyContinue)
    Write-Host "[NARIS] Runtime log: $($logFile.FullName)"
    if ($fatal.Count -gt 0) {
        Write-Warning 'New fatal signatures were detected. Game process existence does not prove runtime health.'
        $fatal | Select-Object -First 5 | ForEach-Object { Write-Warning $_.Line.Trim() }
    } else {
        Write-Host '[NARIS] No fatal signatures in the newest available log (visual QA still required).'
    }
} else {
    Write-Warning 'No fresh game log was found at the common locations. Visual/runtime verification is still required.'
}
if ($process.HasExited) {
    Write-Host "[NARIS] Child game process detected (PID $($activeGame[0].Id)). Confirm menu visibility manually."
} else {
    Write-Host "[NARIS] Game process running (PID $($process.Id)). Confirm menu visibility manually."
}
