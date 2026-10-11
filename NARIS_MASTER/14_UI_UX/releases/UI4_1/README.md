# CALL OF NARIS — UI4.1 Production Patch (safe launcher repair)

Target: the **separate local** Unreal Engine 5.7 project at C:\Users\Admin\NARIS (NARIS.uproject). This is distinct from the repository's unreal/NARIS_W04/NARIS_W04.uproject bootstrap.

## Package and launch (local UE 5.7 project)

    Set-ExecutionPolicy -Scope Process Bypass
    .\Tools\Apply-UI4_1.ps1 -ProjectRoot 'C:\Users\Admin\NARIS' -EngineRoot 'C:\Program Files\Epic Games\UE_5.7'

The guarded script checks source markers and engine prerequisites **before mutation**, backs up affected source, preserves the Direct Play guard, builds NARISEditor, performs BuildCookRun (including the -package flag), searches the archive recursively for NARIS.exe, launches that executable, and checks **fresh** runtime logs. It does not forcibly close Unreal Editor; save and close the editor yourself. A previous archive directory is deliberately never overwritten.

If the build directory already exists, move or rename the old Builds\WindowsDevelopment_UI4_1 folder **without deleting it**, then rerun.

## Start an existing package without rebuilding

Run from the repository root:

    .\tools\windows\Start-NarisGame.ps1 -ProjectRoot 'C:\Users\Admin\NARIS'

For diagnostics without launching, add -ListOnly. To launch a specific package, add -Executable 'C:\absolute\path\NARIS.exe'.

## Validation limits

The log validator verifies startup markers and rejects critical error signatures from a log written during the current run. It does **not** prove menu visibility, click-through, 16:9/21:9/32:9 screenshots, lighting quality, or that the approved new UI art has been integrated into Unreal.

If source anchors differ, the script stops; do not force a blind patch. Restore the newest backup with Tools\Rollback-UI4_1.ps1 when necessary.
