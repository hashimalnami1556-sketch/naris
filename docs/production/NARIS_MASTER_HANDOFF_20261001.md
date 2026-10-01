# NARIS Master Handoff — 2026-10-01

## Purpose
Canonical handoff index for the current CALL OF NARIS production repository. This document records verified project state and prevents older local bundles from overwriting newer GitHub work.

## Canonical repository
- Repository: hashimalnami1556-sketch/naris
- Default branch: main
- Production source of truth: GitHub
- Primary engine: Unreal Engine 5.x
- Primary platform: Windows PC
- Primary vertical slice: W04 / Ashen Forest, with Ashen Wastes/Aetheria production data retained as active design inputs.

## Verified production data already on main
- Docs/AETHERIA_MASTER_EXECUTION.md
- Content/Data/AetheriaBossRoster.json
- Content/Data/AetheriaRealms.json
- Content/Data/AetheriaAudioStates.json
- Content/Data/AetheriaPerformanceBudget.json

## Active integration streams discovered 2026-10-01
- codex/naris-product-context-20260929
- codex/naris-product-design-meshy-game-studio
- feat/asset-generation-pipeline-v1
- feat/w04-asset-expansion
- feature/runtime-core-v2
- integration/ashen-wastes-playable-slice-0-1
- integration/desktop-audit-20260927
- integration/naris-master-0-2
- ui/naris-runtime-interface-foundation
- unity/cross-platform-systems-20260929
- fix/w04-ue57-build

## Local Unreal build state previously verified
The workstation project at C:\Users\Admin\NARIS previously completed Build/Cook/Stage/Pak/Archive successfully for Windows Development. The known tested local commit was 7e9904a. This SHA may belong to the workstation history and must not be force-applied over main without comparison.

## Asset handoff inventory available from the conversation
- 14 reference images
- 1 reference PDF
- 2 MP4 generated/marketing references
- design, identity, character, marketing, and integration text sources
- NARIS_MASTER_COMPLETE_HANDOFF_2026-09-27.zip generated as an external handoff bundle

Binary conversation attachments are not represented here as fake .uasset/.umap files. They must be imported through the asset pipeline or uploaded as real binaries before being marked repository-complete.

## Integration policy
1. Never force-push main.
2. Do not wholesale-merge divergent runtime/rig branches.
3. Compare each integration branch against main.
4. Cherry-pick or merge coherent batches only.
5. Build and run automation after C++/runtime batches.
6. Validate asset registry and provenance after art imports.
7. Keep generated Builds, Intermediate, Saved and DerivedDataCache out of source control unless explicitly packaged as a release artifact.

## Completion gates
- Source: compile clean.
- Runtime: packaged executable smoke-tested.
- Combat: hit timing/attack windows validated, not only instant damage calls.
- AI: attack-token cap verified under encounter load.
- Characters: production skeletal meshes, rigs, animation sets and LODs imported.
- World: W04/Ashen slice playable end-to-end.
- UI: frontend/HUD/pause/settings/save flows validated.
- Audio/VFX: runtime state transitions implemented, not logging-only stubs.
- Performance: 1080p/60 target profiled on target-class hardware.
- Shipping: clean Shipping BuildCookRun and release checklist.

This file is the repository-level handoff index. Detailed implementation remains in the canonical production documents and data registries.
