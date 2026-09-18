@echo off
setlocal
set "ROOT=%~dp0.."
set "UPROJECT=%ROOT%\NARIS_W04.uproject"
if not exist "%UPROJECT%" (echo ERROR: Project not found & exit /b 1)
set "UE=%ProgramFiles%\Epic Games\UE_5.4"
if not exist "%UE%\Engine\Build\BatchFiles\RunUAT.bat" (
  echo ERROR: UE 5.4 not found at "%UE%"
  echo Set UE_ROOT to your Unreal Engine installation and rerun.
  exit /b 2
)
call "%UE%\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun -project="%UPROJECT%" -noP4 -platform=Win64 -clientconfig=Shipping -build -cook -stage -pak -archive -archivedirectory="%ROOT%\Build\Packaged"
if errorlevel 1 exit /b %errorlevel%
echo NARIS W04 package complete.
