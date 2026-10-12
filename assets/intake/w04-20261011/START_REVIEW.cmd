@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\..\tools\windows\Invoke-NarisUploadedCandidates.ps1" %*
if errorlevel 1 (echo Review setup failed. Read the error above. & pause & exit /b 1)
endlocal
