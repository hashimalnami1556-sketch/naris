$ErrorActionPreference='Stop'
$Project='C:\Users\Admin\NARIS\NARIS.uproject'
$Editor='C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe'
$Py='C:\Users\Admin\NARIS\Pipeline\Unreal\import_exchange.py'
Start-Process -FilePath $Editor -ArgumentList @($Project,'-ExecutePythonScript='+$Py)
