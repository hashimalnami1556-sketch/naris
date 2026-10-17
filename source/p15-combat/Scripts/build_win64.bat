@echo off
setlocal
if "%~4"=="" (
    echo Usage: build_win64.bat project.uproject UE_5.7 /Game/Maps/Test SourceAssets
    exit /b 2
)
if "%~5"=="" (
    powershell.exe -NoProfile -File "%~dp0build_win64.ps1" -Project "%~1" -EngineRoot "%~2" -Map "%~3" -AssetDir "%~4"
) else (
    powershell.exe -NoProfile -File "%~dp0build_win64.ps1" -Project "%~1" -EngineRoot "%~2" -Map "%~3" -AssetDir "%~4" -ImportSpec "%~5"
)
exit /b %ERRORLEVEL%
