param(
  [switch]$CheckOnly,
  [switch]$RunAutomation,
  [int]$MinDiskGiB = 30,
  [int]$MinFreeRamGiB = 8
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = $env:NARIS_UE57_PROJECT_ROOT
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {throw 'Set NARIS_UE57_PROJECT_ROOT to actual project root'}
$EngineRoot = $env:UNREAL_ENGINE_ROOT
if ([string]::IsNullOrWhiteSpace($EngineRoot)) {throw 'Set UNREAL_ENGINE_ROOT to actual UE5.7 installation'}
$Project = Join-Path $ProjectRoot 'NARIS.uproject'
$BuildBat = Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat'
$EditorCmd = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$Evidence = Join-Path $ProjectRoot 'docs\changes\NET-001\revive3d_20261121'
$Required = @($Project,$BuildBat,$EditorCmd,
  (Join-Path $ProjectRoot 'Source\NARIS\Multiplayer\NarisCoopCharacter.cpp'),
  (Join-Path $ProjectRoot 'Source\NARIS\Multiplayer\NarisCoopCharacter.h'),
  (Join-Path $ProjectRoot 'Source\NARIS\Tests\NarisCoopTests.cpp'))
$Missing = @($Required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
$DiskFree = (Get-PSDrive -Name C -PSProvider FileSystem).Free
$Os = Get-CimInstance Win32_OperatingSystem
$MemFree = [double]$Os.FreePhysicalMemory * 1KB
$Busy = @(Get-CimInstance Win32_Process | Where-Object {
  $_.Name -match '^(UnrealEditor(-Cmd)?|ShaderCompileWorker|UnrealBuildTool|AutomationTool|MSBuild|cl|link)\.exe$'
})
$Reasons = @()
if ($Missing.Count -gt 0) {$Reasons += 'MISSING_REQUIRED_FILES'}
if ($DiskFree -lt ($MinDiskGiB * 1GB)) {$Reasons += 'LOW_DISK'}
if ($MemFree -lt ($MinFreeRamGiB * 1GB)) {$Reasons += 'LOW_RAM'}
if ($Busy.Count -gt 0) {$Reasons += 'COMPETING_BUILD'}
$Result = [ordered]@{
  check='NET-001 source hardening gate'
  utc=(Get-Date).ToUniversalTime().ToString('o')
  free_disk_gib=[math]::Round($DiskFree / 1GB,2)
  required_disk_gib=$MinDiskGiB
  free_ram_gib=[math]::Round($MemFree / 1GB,2)
  required_ram_gib=$MinFreeRamGiB
  competing_processes=$Busy.Count
  missing_required_files=$Missing.Count
  eligible=($Reasons.Count -eq 0)
  blockers=@($Reasons)
  build_run=$false
  automation_run=$false
  two_client_validation=$false
}
$Result | ConvertTo-Json -Depth 4
if ($Reasons.Count -gt 0) {exit 2}
if ($CheckOnly) {exit 0}
if (-not $RunAutomation) {throw 'Use -RunAutomation explicitly to start UE build/test'}
if (-not (Test-Path -LiteralPath $Evidence)) {throw 'NET001 evidence folder missing'}
$BuildLog = Join-Path $Evidence 'NET001_editor_build_after_hardening.log'
$TestLog = Join-Path $Evidence 'NET001_unreal_automation_after_hardening.log'
if ((Test-Path $BuildLog) -or (Test-Path $TestLog)) {
  throw 'Existing evidence log; refuse to overwrite'
}
& $BuildBat NARISEditor Win64 Development "-Project=$Project" '-WaitMutex' '-NoHotReload' *>&1 | Out-File -FilePath $BuildLog -Encoding utf8
if ($LASTEXITCODE -ne 0) {throw 'UE_BUILD_FAILED_READ_LOG'}
$ReportPath = Join-Path $Evidence 'UE_AUTOMATION_REPORT'
& $EditorCmd $Project '-unattended' '-nop4' '-nullrhi' '-nosound' '-log' '-ExecCmds=Automation RunTest NARIS.Coop.Character;Quit' "-ReportExportPath=$ReportPath" *>&1 | Out-File -FilePath $TestLog -Encoding utf8
if ($LASTEXITCODE -ne 0) {throw 'UE_TEST_COMMAND_FAILED_READ_LOG'}
if (-not (Test-Path -LiteralPath (Join-Path $ReportPath 'index.json'))) {
  throw 'UE_AUTOMATION_REPORT_MISSING_DO_NOT_CLAIM_PASS'
}
Write-Output 'BUILD_COMPLETED_TEST_REPORT_PRESENT_REVIEW_TEST_FAILURES_MANUALLY'
Write-Output 'NETWORK_SERVER_PLUS_TWO_CLIENTS_STILL_REQUIRED_FOR_CLOSURE'

[executed on device: AsusRog (81c43ddb-199e-4bc1-9944-e3faf018908f)]