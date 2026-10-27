# NARIS UE5.7 Master Integration State — 2026-10-28

Canonical production runtime: Unreal Engine 5.7 / unreal/NARIS_W04.

## Integrated into main
- Native P20 menu/UI and New Game -> W04_AshenForest production routing.
- Stage26/27/28 W04 map/build authoring baseline.
- Stage30-33 runtime, animation-driven combat, PBR/material binding and fail-closed release gates.
- PR #63 Stage32 hardened combat component and CI contracts.
- PR #65 Stage34 animation/material audit and Windows build gate.
- PR #66 Stage35 guarded UE editor/asset gate.
- PR #67 Stage36 asset-class inventory.
- PR #69 Stage28 PBR/animation/cinematic handoff documentation.
- PR #70 Stage29 corrected W04 placement coordinates.
- PR #71 Stage29 map/PBR/animation QA gate.
- Stage37 native combat hit-window AnimNotifyState and animation linkage audit, rebased into main.\n- W04 villain runtime: native villain character C++, encounter roster, authoring/import scripts and guarded Windows integration.
- Stage33 asset binder: material instances -> canonical PBR textures and Hero AnimBP/Montage validation.

## Deliberately not merged into canonical runtime
- Godot prototype branches.
- Browser/Web3D prototype branches.
- Unity prototype branches.
- Reference-board/image-only assets that have not been converted, rigged, imported and engine-validated.
- Binary delivery claims that exist only in external ZIP artifacts and are not present in repository history.

## Runtime truth
Repository integration is complete at source/contract level. Unreal-generated .uasset/.umap state, UE5.7 compile, PIE gameplay, visual PBR QA, packaged Windows Shipping EXE and performance evidence remain fail-closed until executed on the authorized Windows Unreal host.

## Next executable chain
Invoke-NarisStage33BindAssets.ps1
-> Invoke-NarisStage30Runtime.ps1
-> Invoke-NarisStage32Release.ps1
-> interactive PIE/full-loop QA
-> Windows Shipping artifact + SHA256.


## Conflict policy after consolidation
PR #18, #35 and #42 are not merged wholesale because they now conflict with the newer canonical main. Their useful fixes must be forward-ported individually only when current-source inspection proves the fix is still absent. This prevents regression of the newer menu, combat, map, animation and release pipeline.
