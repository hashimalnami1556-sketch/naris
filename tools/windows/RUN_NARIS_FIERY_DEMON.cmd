@echo off
setlocal EnableExtensions
REM NARIS W04 Fiery Demon: one-click build + launch from real UE5.7 sources.
REM No executable is bundled in Git; this launcher compiles and cooks it.
set "REPO=%~dp0..\.."
set "MODEL=%REPO%\Assets\NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb"
if not exist "%MODEL%" set "MODEL=%USERPROFILE%\NARIS\Assets\NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb"
if not exist "%MODEL%" set "MODEL=%USERPROFILE%\Downloads\NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb"
if not exist "%MODEL%" (
  echo [NARIS ERROR] Animated demon GLB is missing.
  echo Extract NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb to:
  echo   %USERPROFILE%\NARIS\Assets\
  echo Then launch this script again.
  exit /b 2
)
set "ENVIRONMENT=%REPO%\Assets\Environmental 1.glb"
if not exist "%ENVIRONMENT%" set "ENVIRONMENT=%USERPROFILE%\NARIS\Assets\Environmental 1.glb"
set "SCRIPT=%~dp0Invoke-NarisFieryDemonBuild.ps1"
if not exist "%SCRIPT%" (
  echo [NARIS ERROR] Build script not found: %SCRIPT%
  exit /b 3
)
if exist "%ENVIRONMENT%" (
  powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -RepoRoot "%REPO%" -DemonGlb "%MODEL%" -EnvironmentGlb "%ENVIRONMENT%" -Package -Launch
) else (
  powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -RepoRoot "%REPO%" -DemonGlb "%MODEL%" -Package -Launch
)
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" echo [NARIS ERROR] Build or launch failed. Exit code: %RESULT%
exit /b %RESULT%
