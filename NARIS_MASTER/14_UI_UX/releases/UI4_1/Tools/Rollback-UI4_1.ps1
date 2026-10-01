param([string]$ProjectRoot='C:\Users\Admin\NARIS')
$ErrorActionPreference='Stop'
$backupRoot=Join-Path $ProjectRoot 'Backups\UI4_1'
$latest=Get-ChildItem $backupRoot -Directory -ErrorAction Stop | Sort-Object Name -Descending | Select-Object -First 1
if(!$latest){throw 'No UI4.1 backup found.'}
Copy-Item (Join-Path $latest.FullName 'NarisHUD.h') (Join-Path $ProjectRoot 'Source\NarisCore\Public\NarisHUD.h') -Force
Copy-Item (Join-Path $latest.FullName 'NarisHUD.cpp') (Join-Path $ProjectRoot 'Source\NarisCore\Private\NarisHUD.cpp') -Force
Copy-Item (Join-Path $latest.FullName 'NarisGameModeBase.cpp') (Join-Path $ProjectRoot 'Source\NarisCore\Private\NarisGameModeBase.cpp') -Force
Copy-Item (Join-Path $latest.FullName 'DefaultInput.ini') (Join-Path $ProjectRoot 'Config\DefaultInput.ini') -Force
"Restored $($latest.FullName)"
