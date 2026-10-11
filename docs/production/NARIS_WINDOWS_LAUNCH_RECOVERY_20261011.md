# NARIS — Windows launch diagnostics and UI4.1 script repair — 2026-10-11

## Scope and reproducible defects

The earlier quick-launch PowerShell command looked only for NARIS.exe in one Builds tree; it missed the repository W04 name NARIS_W04.exe and staged/archived build paths. It also did not diagnose early process termination or fatal logs.

The existing UI4_1/Tools/Apply-UI4_1.ps1 assumed NARIS.exe was archived at the output root, omitted an explicit -package flag, forcibly terminated all open Unreal Editor processes, and validated a fixed log path without requiring a log from this launch. These failures could cause incorrect startup reports and loss of unsaved editor state.

## Repairs in source

- tools/windows/Start-NarisGame.ps1: finds NARIS.exe, NARIS_W04.exe or NARSIC.exe within common package roots, launches the newest, handles short-lived bootstrap processes, and warns about fresh fatal logs. Supports -ListOnly and an explicit -Executable.
- NARIS_MASTER/14_UI_UX/releases/UI4_1/Tools/Apply-UI4_1.ps1: preflight checks source and engine prerequisites, refuses to kill Unreal Editor, preserves existing build archives, adds -package, discovers archived executable recursively, and checks current launch status.
- NARIS_MASTER/14_UI_UX/releases/UI4_1/Tools/Validate-UI4_1.ps1: searches both package and local app-data logs, waits for startup markers, and filters out stale logs when given the launch timestamp.
- tools/ci/test_windows_naris_launch_contract.py: source-level regression checks.

The existing NARIS_UI4_1_Production_Patch.zip binary archive has NOT been regenerated in this source-only change. Use the corrected tracked Tools scripts from this revision, not a stale previously downloaded ZIP.

## Evidence and limitations

Source-level defects are addressed, but game crashes, asset failures, missing production maps, firewall dialogues, and actual menu rendering can only be validated by Unreal 5.7 build/cook/package and workstation execution. The AsusRog remote control service rejected commands because the account reached its usage limit; no new Windows runtime test is claimed.

The existing [NARSIC UI runtime repair](NARSIC_UI_RUNTIME_REPAIR_20261011.md) must still pass packaged UI screenshots, menu click-through, controller navigation, lighting and smoke tests. Passing log markers is NOT visual acceptance.

## Local commands

From the repository root:

    .\tools\windows\Start-NarisGame.ps1 -ProjectRoot 'C:\Users\Admin\NARIS_CANON' -ListOnly
    .\tools\windows\Start-NarisGame.ps1 -ProjectRoot 'C:\Users\Admin\NARIS_CANON'

The launcher now defaults to this canonical checkout, also discovers nested W04 staged packages and direct Win64 Development/Shipping executables, and searches the checkout containing the launcher. Automatic selection uses executable modification time; it does not establish a verified release version. Use `-Executable` to choose a reviewed package explicitly. Bootstrap acceptance requires an actual child process with an executable inside the selected package directory; a different recently started NARIS instance is not evidence of success. Windows execution of these follow-up changes is still pending.

If no package exists, launch the guarded UI4.1 workflow from its release directory (after saving and closing Unreal Editor):

    Set-Location 'NARIS_MASTER\14_UI_UX\releases\UI4_1'
    .\Tools\Apply-UI4_1.ps1 -ProjectRoot 'C:\Users\Admin\NARIS'

If the workflow reports an existing output directory, preserve/move that older build before retrying. For crash triage, collect the NEW Saved\Logs file and relevant Saved\Crashes content; do not infer a successful game launch from source checks.
