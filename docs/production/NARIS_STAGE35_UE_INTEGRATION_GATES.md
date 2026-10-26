# Stage35 — UE5.7 compilation and asset linkage gate

This change connects a **real Windows build command** to a **non-destructive Unreal Editor Python asset audit**.

### Execution on the connected Windows machine
```powershell
powershell -ExecutionPolicy Bypass -File tools/windows/Invoke-NarisStage35EditorGate.ps1 -RepoRoot "D:\UE_Projects\naris" -UnrealEngineRoot "C:\Program Files\Epic Games\UE_5.7"
```
Adjust the two paths to actual installations. The script stops if the editor build fails, the Python audit crashes, or required content folders are missing/empty. It does **not** silently declare success. Logs and JSON go to `unreal/NARIS_W04/Saved/TestReports`.

### What is wired
- Build.bat compiles `NARIS_W04Editor` before attempting any asset audit.
- UnrealEditor-Cmd executes the audit, which checks existing character, map, animation and material folders.
- The audit optionally creates **one new preview material** in a quarantined import folder, without overwriting assets.
- The PowerShell gate reads the JSON report and fails on blockers.

### Not done
- It does not create Animation Blueprints or Montages automatically, because the existing skeletons and animations have not been inspected in the editor.
- It does not bind Stage32 C++ to a specific Blueprint character or perform PIE; that requires real assets and a live Unreal session.
- It does not import Stage29/30 GLBs from this repository, since those binaries have not been committed.
- It does not produce or certify a Windows EXE.
- Do not merge until UE5.7 API compatibility and editor execution are verified.

### Known limitations
The preview material call may require UE API adjustments for `MaterialEditingLibrary`; any failure is a blocking error. Source-only CI is not equivalent to an Unreal compile.
