# Stage 8 — Final Map + Windows EXE Gate

## Objective
Close the two release blockers:
1. /Game/NARIS/W04/Maps/W04_AshenForest
2. A verified Windows Shipping executable.

## Current truth
The repository has UE 5.7 source and packaging infrastructure, but the final production .umap and a verified packaged EXE are not yet runtime evidence.

## Promotion rule
W04_Prototype is development smoke only.
W04_AshenForest_Blockout is assembly only.
W04_AshenForest is the only Shipping map.

The Windows script refuses to package if W04_AshenForest.umap is absent, runs the shipping-map validator, executes BuildCookRun, requires a NARIS *.exe, and prints SHA-256.

No EXE is marked complete until a self-hosted Windows Unreal runner or the authorized workstation actually passes this gate.

## Activated execution path — 2026-10-26

All canonical W04 zones are authorized for implementation through the existing [layout](../../NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json). No asset QA status is advanced by this authorization.

Run from the repository root on a Windows UE5.7 host:

```powershell
.\tools\windows\Build-NarisWindows.ps1 -Configuration Development
.\tools\windows\Build-NarisWindows.ps1 -Configuration Shipping
```

The wrapper verifies the engine version and routes to the canonical scripts; it does not call a synthetic commandlet or bypass animation/material/core-asset/presentation gates. Shipping requires the saved production map. Each package invocation has an isolated archive; historical reports are moved aside before new strict reports are collected. The output hash identifies the current executable, not a cached one.

The source preflight refuses to promote BasicShapes, duplicate/mis-typed gameplay labels and review/blockout content. Renaming blockout actors cannot substitute for production geometry. `naris_stage8_promote_final_map.py` only copies an already structurally compliant authored source and does not overwrite an existing final map.

The Windows Shipping workflow runs its source checks automatically on relevant main pushes, then requires `[self-hosted, windows, unreal]`. An offline workstation or absent runner blocks the engine phase. Package creation does not automatically approve public release; packaged gameplay, save/load, EN/AR and target-device performance remain separate acceptance evidence.
