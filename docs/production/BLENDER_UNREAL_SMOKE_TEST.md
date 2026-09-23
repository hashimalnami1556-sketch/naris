# Blender -> Unreal smoke test

This is the executable bridge between the NARIS Blender DCC workflow and the canonical Unreal 5.4 project.

## Inputs
- a source `.blend` file;
- an immutable NARIS asset ID present in the production registry;
- Blender available through `BLENDER_EXE` or a standard installation path;
- Unreal Engine 5.4 root through `UNREAL_ENGINE_ROOT`.

## Stages
1. `tools/blender/naris_export.py` validates source objects and emits FBX/GLB plus a manifest.
2. The manifest follows `schemas/naris_blender_exchange.schema.json`.
3. `naris_import_blender_exchange.py` refuses failed manifests, imports FBX/GLB, adds source metadata, and saves under `/Game/NARIS/Imported/<world>/<asset-id>`.
4. `Invoke-NarisBlenderUnrealSmoke.ps1` executes both applications and fails on a non-zero exit.

## Windows invocation

```powershell
$env:UNREAL_ENGINE_ROOT = "C:\Program Files\Epic Games\UE_5.4"
$env:BLENDER_EXE = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

.\tools\windows\Invoke-NarisBlenderUnrealSmoke.ps1 \
  -RepoRoot "C:\Users\Admin\NARIS" \
  -BlendFile "C:\path\NARIS-W04-PRP-WAYSTONE-0001.blend" \
  -AssetId "NARIS-W04-PRP-WAYSTONE-0001"
```

A passing script is DCC/export/import evidence only. Material parity, collision quality, skeletal correctness, animation, Nanite/LOD policy and in-level gameplay still require editor QA.
