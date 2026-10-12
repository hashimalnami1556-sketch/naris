param(
    [string[]]$SearchRoots = @(
        "C:\\actions-runner",
        "C:\\github-runner",
        "C:\\Users\\Admin\\actions-runner",
        "C:\\Users\\Admin\\github-runner",
        "C:\\Users\\Admin\\OneDrive\\actions-runner"
    )
)

$ErrorActionPreference = "Stop"

$report = [ordered]@{
    schema = "naris.self-hosted-runner-recovery.v1"
    product = "CALL OF NARIS"
    checked_at = (Get-Date).ToUniversalTime().ToString("o")
    services = @()
    runner_processes = @()
    runner_roots = @()
    actions = @()
    status = "UNKNOWN"
}

$services = @(Get-Service -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -like "actions.runner.*" -or
    $_.DisplayName -like "*GitHub Actions Runner*"
})

foreach ($svc in $services) {
    $entry = [ordered]@{
        name = $svc.Name
        display_name = $svc.DisplayName
        status_before = [string]$svc.Status
        status_after = [string]$svc.Status
        start_attempted = $false
        start_succeeded = $false
    }

    if ($svc.Status -ne "Running") {
        $entry.start_attempted = $true
        try {
            Start-Service -Name $svc.Name -ErrorAction Stop
            $svc.WaitForStatus("Running", [TimeSpan]::FromSeconds(15))
            $entry.start_succeeded = $true
            $entry.status_after = "Running"
            $report.actions += "Started service $($svc.Name)"
        } catch {
            $entry.status_after = [string](Get-Service -Name $svc.Name -ErrorAction SilentlyContinue).Status
            $report.actions += "Failed to start service $($svc.Name): $($_.Exception.Message)"
        }
    }

    $report.services += $entry
}

$proc = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -in @("Runner.Listener","Runner.Worker","runsvc","run")
})
foreach ($p in $proc) {
    $report.runner_processes += [ordered]@{
        id = $p.Id
        process_name = $p.ProcessName
        start_time = try { $p.StartTime.ToUniversalTime().ToString("o") } catch { $null }
    }
}

$roots = @()
foreach ($root in $SearchRoots) {
    if (Test-Path -LiteralPath $root) {
        $roots += (Resolve-Path -LiteralPath $root).Path
    }
}

# Find configured runner roots beyond the common locations without scanning entire disks.
$parents = @(
    "C:\\Users\\Admin",
    "C:\\Users\\Admin\\OneDrive",
    "C:\\"
)
foreach ($parent in $parents) {
    if (-not (Test-Path -LiteralPath $parent)) { continue }
    try {
        Get-ChildItem -LiteralPath $parent -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match "actions.?runner|github.?runner" } |
            ForEach-Object { $roots += $_.FullName }
    } catch {}
}
$roots = @($roots | Sort-Object -Unique)

foreach ($root in $roots) {
    $runnerJson = Join-Path $root ".runner"
    $serviceCmd = Join-Path $root "svc.cmd"
    $runCmd = Join-Path $root "run.cmd"

    $configured = Test-Path -LiteralPath $runnerJson
    $config = $null
    if ($configured) {
        try {
            $config = Get-Content -Raw -LiteralPath $runnerJson | ConvertFrom-Json
        } catch {}
    }

    $report.runner_roots += [ordered]@{
        path = $root
        configured = $configured
        agent_name = if ($config) { $config.agentName } else { $null }
        pool_id = if ($config) { $config.poolId } else { $null }
        server_url = if ($config) { $config.serverUrl } else { $null }
        svc_cmd = Test-Path -LiteralPath $serviceCmd
        run_cmd = Test-Path -LiteralPath $runCmd
    }
}

$runningService = @($report.services | Where-Object { $_.status_after -eq "Running" }).Count -gt 0
$runningProcess = @($report.runner_processes).Count -gt 0
$configuredRoot = @($report.runner_roots | Where-Object { $_.configured }).Count -gt 0

if ($runningService -or $runningProcess) {
    $report.status = "RUNNER_ACTIVE"
} elseif ($configuredRoot) {
    $report.status = "CONFIGURED_BUT_NOT_ACTIVE"
} else {
    $report.status = "RUNNER_NOT_REGISTERED"
}

$outDir = "C:\\Users\\Admin\\OneDrive\\NARIS_MASTER_BUNDLE\\Game\\NARIS_UE57\\Reports"
if (Test-Path -LiteralPath (Split-Path $outDir -Parent)) {
    New-Item -ItemType Directory -Force $outDir | Out-Null
    $out = Join-Path $outDir "SELF_HOSTED_RUNNER_DIAGNOSTIC.json"
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $out -Encoding UTF8
    Write-Host "NARIS_RUNNER_REPORT=$out"
}

Write-Host ($report | ConvertTo-Json -Depth 8)

if ($report.status -eq "RUNNER_ACTIVE") {
    Write-Host "NARIS_RUNNER_READY=1"
    exit 0
}
if ($report.status -eq "CONFIGURED_BUT_NOT_ACTIVE") {
    Write-Error "GitHub Actions runner is configured but could not be activated."
    exit 20
}

Write-Error "No registered GitHub Actions runner was found. Registration requires a fresh GitHub runner token; this script intentionally will not fabricate one."
exit 21
