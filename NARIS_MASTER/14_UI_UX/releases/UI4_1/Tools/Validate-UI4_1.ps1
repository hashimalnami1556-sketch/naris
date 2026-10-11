param(
    [string]$ProjectRoot = 'C:\Users\Admin\NARIS',
    [string]$BuildName = 'WindowsDevelopment_UI4_1',
    [datetime]$LaunchedAtUtc = [DateTime]::MinValue,
    [ValidateRange(0, 180)][int]$WaitSeconds = 45
)
$ErrorActionPreference = 'Stop'

$archive = Join-Path $ProjectRoot "Builds\$BuildName"
$roots = @($archive)
if ($env:LOCALAPPDATA) {
    $roots += (Join-Path $env:LOCALAPPDATA 'NARIS\Saved\Logs')
    $roots += (Join-Path $env:LOCALAPPDATA 'UnrealGame\Saved\Logs')
}
$deadline = (Get-Date).AddSeconds($WaitSeconds)
$log = $null
$text = ''

# Only accept logs updated during this run when the launcher passes its UTC start time.
do {
    $logs = @(
        foreach ($root in $roots) {
            if (Test-Path -LiteralPath $root -PathType Container) {
                Get-ChildItem -LiteralPath $root -Filter '*.log' -File -Recurse -ErrorAction SilentlyContinue |
                    Where-Object {
                        $_.Name -match '^(NARIS|UnrealGame).*\.log$' -and
                        ($LaunchedAtUtc -eq [DateTime]::MinValue -or
                            $_.LastWriteTimeUtc -ge $LaunchedAtUtc.ToUniversalTime().AddSeconds(-2))
                    }
            }
        }
    )
    $logs = @($logs | Sort-Object LastWriteTimeUtc -Descending)
    foreach ($candidate in $logs) {
        $candidateText = Get-Content -LiteralPath $candidate.FullName -Raw -ErrorAction SilentlyContinue
        if ($candidateText -match 'NARIS_FRONTEND READY' -and
            $candidateText -match 'NARIS_RUNTIME_READY') {
            $log = $candidate
            $text = $candidateText
            break
        }
    }
    if ($log -or (Get-Date) -ge $deadline) { break }
    Start-Sleep -Seconds 2
} while ($true)

if (-not $log) {
    throw "No fresh NARIS log containing both readiness markers within $WaitSeconds seconds. Searched: $($roots -join '; ')"
}
$checks = [ordered]@{
    FrontEndReady = ($text -match 'NARIS_FRONTEND READY')
    RuntimeReady = ($text -match 'NARIS_RUNTIME_READY')
    NoForcedDirectPlay = ($text -notmatch 'NARIS_DIRECT_PLAY')
    NoFatal = ($text -notmatch '(?im)Fatal error:|Unhandled Exception|Assertion failed:|LowLevelFatalError|LogWindows: Error:')
}
Write-Host "[NARIS] Validated fresh log: $($log.FullName)"
$checks.GetEnumerator() | ForEach-Object { '{0}={1}' -f $_.Key, $_.Value }
if ($checks.Values -contains $false) { exit 2 }
'NARIS_UI4_1_LOG_GATE PASS - visual UI acceptance still pending'
