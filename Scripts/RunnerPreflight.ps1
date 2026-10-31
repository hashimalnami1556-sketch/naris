# CI-001: Read-only preflight for a dedicated Windows GitHub Actions runner.
# Run in PowerShell on ASUSROG. No secrets, installation, or system changes.
$ErrorActionPreference = 'Continue'
Write-Host '=== NARIS RUNNER PREFLIGHT ==='
Write-Host ('Host: ' + $env:COMPUTERNAME)
Write-Host ('Identity: ' + [Security.Principal.WindowsIdentity]::GetCurrent().Name)
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$admin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Host ('Administrator token: ' + $admin)
if ($admin) { Write-Warning 'Do not run a public-repository self-hosted runner under this administrator account.' }
foreach ($name in @('git','git-lfs','python','tailscale','ssh')) {
  $cmd = Get-Command $name -ErrorAction SilentlyContinue
  Write-Host ('{0}: {1}' -f $name, $(if ($cmd) { $cmd.Source } else { 'NOT FOUND' }))
}
$paths = @(
  'C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\nar pic\Narsic\Narsic',
  'C:\MyGame'
)
foreach ($p in $paths) {
  Write-Host ('Project candidate: {0} Exists={1}' -f $p, (Test-Path -LiteralPath $p))
}
Get-ChildItem 'C:\Program Files\Epic Games' -Directory -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -like 'UE_*' } |
  ForEach-Object { Write-Host ('Unreal install: ' + $_.FullName) }
Write-Host 'Runner status: NOT INSTALLED BY THIS SCRIPT'
Write-Host 'Next: provision a dedicated non-admin Windows account and restrict repo workflow permissions before registering.'
