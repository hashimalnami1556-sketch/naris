# NARIS Unreal localization

Target: `NARIS_Game`

Native culture: English (`en`)  
Initial foreign culture: Arabic (`ar`)

The C++ runtime prompts and smoke HUD use `NSLOCTEXT("NARIS", key, source)`.
The checked-in PO files provide the first English/Arabic catalog for those keys.

Run on Windows:

```powershell
$env:UNREAL_ENGINE_ROOT = "C:\Program Files\Epic Games\UE_5.4"
.\tools\windows\Invoke-NarisLocalization.ps1 -RepoRoot "C:\Users\Admin\NARIS"
```

This runs the Unreal GatherText pipeline: source/assets -> manifest/archive -> PO
import/export -> compiled localization resources.

Source readiness is not Arabic rendering QA. Arabic font coverage, shaping, RTL
layout, controller glyph placement, and UMG overflow still require engine/editor
verification before localization can be marked production-ready.
