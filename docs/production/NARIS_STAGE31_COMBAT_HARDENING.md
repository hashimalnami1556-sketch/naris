# Stage31 — Combat reliability hardening

Status: **offline C++ source delivered; engine compile and PIE NOT run**. Local package: `NARIS_STAGE31_COMBAT_HARDENING.zip` (2 C++ source files, integration instructions, contract tests, QA).

## Actual implementation changes
- New `UNarisStage31CombatComponent` with health, stamina, attack, dodge, recovery, death.
- `TryAttackMontage` / `TryDodgeMontage`: montage playback must succeed before stamina cost is deducted; no stamina cost on failure.
- Animation notify gated melee sweep, single hit per target per attack, attack interruption clears window and target cache.
- Dodge invulnerability window, finite positive damage validation, stamina regeneration during idle, independent recovery state.
- Blueprint integration requires Montage-ended and Montage-interrupted callbacks; missing callbacks can leave an action active.
- Friendly-fire/team handling, authoritative networking, animation retargeting, motion quality, AI and full production integration remain outstanding.

## Verified locally
Eight source-contract tests passed. **These are not Unreal compilation or runtime tests.** Host `AsusRog` was offline at check time.

## Critical release blockers
1. Copy the package C++ source to `unreal/NARIS_W04/Source/NARIS_W04/Public` and `Private`, and compile with Unreal Engine 5.7. Resolve compile errors.
2. Bind Enhanced Input, AnimMontages and damage-window AnimNotifies in player/enemy Blueprints. Ensure end/interruption callbacks always run.
3. Validate 30/60 FPS, interruption, stamina rollback, friendly fire, death and dodge invulnerability in PIE.
4. Finish W04 production map, source-verified PBR textures and all rig/animation assets before running strict Windows release-candidate pipeline.
5. Do not mark game, map or Windows EXE production ready without actual packaged executable and runtime evidence.

This branch contains a traceable technical handoff note; binary/source bundle is supplied separately for review before importing into canonical engine project.
