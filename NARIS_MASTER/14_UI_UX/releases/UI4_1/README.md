# CALL OF NARIS — UI4.1 Production Patch

Target: Unreal Engine 5.7 project at `C:\Users\Admin\NARIS`.

This package provides a guarded executable production workflow and does not pretend binary Unreal assets exist.

## Run
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\Tools\Apply-UI4_1.ps1
```

The workflow validates UI3 markers, backs up affected files, preserves the front-end Direct Play fix, builds NARISEditor, packages Windows Development, launches NARIS.exe and validates the packaged log.

If source anchors differ, it stops rather than guessing. Use the rollback script to restore the newest backup.
