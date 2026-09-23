# W04 Unreal Editor bootstrap

Purpose: create the first binary Unreal assets needed to exercise the W04 source
contracts on Windows. This is a **runtime-smoke scaffold**, not final level art.

The script creates or loads:

- `/Game/NARIS/W04/Maps/W04_Prototype`
- `/Game/NARIS/W04/Data/DA_BoneBeast_Smoke`
- PlayerStart
- Waystone
- Memory Crystal
- Ash Gate
- Celestial Wolf
- Bone Beast Boss
- a simple engine-cube floor
- basic smoke-test lighting

The layout is deliberately deterministic and simple. Final Ashen Forest authored
level design remains a separate production gate.

## Run on Windows

```powershell
$env:UNREAL_ENGINE_ROOT = "C:\Program Files\Epic Games\UE_5.4"
.\tools\windows\Invoke-NarisW04AuthoringBootstrap.ps1 -RepoRoot "C:\Users\Admin\NARIS"
```

The Bone Beast smoke DataAsset uses a test-only health value so the encounter can
be exercised before production balancing. It is not production tuning.

Success evidence is the generated `.umap/.uasset` content opening successfully in
Unreal Editor and a retained bootstrap log.
