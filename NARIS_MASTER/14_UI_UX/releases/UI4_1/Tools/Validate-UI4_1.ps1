param([string]$ProjectRoot='C:\Users\Admin\NARIS',[string]$BuildName='WindowsDevelopment_UI4_1')
$ErrorActionPreference='Stop'
$log=Join-Path $ProjectRoot "Builds\$BuildName\NARIS\Saved\Logs\NARIS.log"
if(!(Test-Path $log)){ throw "Packaged log not found: $log" }
$t=Get-Content -Raw $log
$checks=[ordered]@{
 FrontEndReady=($t -match 'NARIS_FRONTEND READY')
 RuntimeReady=($t -match 'NARIS_RUNTIME_READY')
 DirectPlayRegression=($t -notmatch 'NARIS_DIRECT_PLAY')
 NoFatal=($t -notmatch '(?im)Fatal error|LogWindows: Error:')
 NoLoadFailure=($t -notmatch '(?im)Failed to load|Failed to find')
}
$checks.GetEnumerator() | ForEach-Object { "{0}={1}" -f $_.Key,$_.Value }
if($checks.Values -contains $false){ exit 2 }
'NARIS_UI4_1_GATE PASS'
