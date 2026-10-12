# NARIS Blender / Unreal Character Intake

The portable batch tools and all six *user-provided* binary assets are delivered in the separately downloadable `NARIS_Character_Intake_20261012.zip` package; binaries are intentionally absent from GitHub until provenance and redistribution rights are verified.

From Windows PowerShell after extracting the package:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_naris_character_intake.ps1 `
 -BlenderExe "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
 -UnrealEditorCmd "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
 -UnrealProject "C:\Users\Admin\NARIS\unreal\NARIS_W04\NARIS_W04.uproject"
```

The packaged scripts run: SHA256 source audit -> Blender USDZ extraction and humanoid auto-rig or source-skin import -> FBX + per-asset QA report -> Unreal skeletal importer -> W04_CharacterIntake_QA review map.

**No automatic production-map mutation**. Artist QA / legal rights gates remain mandatory.
