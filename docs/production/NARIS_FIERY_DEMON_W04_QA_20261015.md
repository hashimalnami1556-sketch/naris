# Fiery Demon — W04 native combat integration status

**Snapshot:** 2026-10-15  
**Branch:** `feat/w04-character-intake-20261012` (PR #39 — remains review-only)  
**Product:** CALL OF NARIS / NARSIC; technical namespace `NARIS`  
**Engine target:** UE 5.7 / Windows / QA map `/Game/NARIS/W04/Maps/L_FieryDemon_QA`.

## Changes confirmed in GitHub source

1. `ABoneBeastBoss::RequestPhaseAttack` is virtual; existing Bone Beast attack mapping remains intact.
2. `ANarisFieryDemonBoss` overrides the attack selection: phase 1 **GroundSmash** (28 damage), phase 2 **EmberNova** (46 damage). Two phases at 55% HP; 6200 max HP.
3. Pending attacks are cancelled on death/phase transition; delayed impact checks melee range and an actual `ECC_Visibility` line trace so a wall blocks impact.
4. Native `BeginPlay()` logs `NARIS_FIERY_DEMON_RUNTIME_READY` **only** when the actor has a SkeletalMesh and Idle, Smash, and Nova animation references. Missing bindings emit `NARIS_FIERY_DEMON_ASSET_BINDING_FAILED`.
5. Windows smoke script requires **both** fresh `LogLoad: LoadMap:` for the exact QA map and the native runtime-ready marker in the same fresh log. Command-line map echoes and stale logs no longer count as launch success.
6. The Unreal import script rejects absent skeletal meshes/required clips and keeps production-map changes opt-in. The alternate animated GLB source is supplied separately; it is not automatically present in the Git repository.

## Verifiable test result

**Workflow:** `NARIS CI` run 38715823076 (2026-10-15).  
**Result:** `tools/ci` suite **390 tests passed**, `tools/assetforge` **6 tests passed**. Unreal project JSON, content validation, MCP build and static Unreal checks passed in their respective jobs/workflows.  
**TDD evidence:** three new combat-regression assertions failed before their fixes; two packaged-map-smoke assertions failed before the log check fix; three native-runtime-marker assertions failed before logging and smoke gate were added.

These are **source-level tests**, NOT an engine compilation, an actual `.umap` creation, AI/playtest evidence, or a packaged Windows smoke result. GitHub-hosted CI deliberately skips the self-hosted Unreal Windows package job on PR runs.

## Next acceptance gates (blocking)

- [ ] Recover/licence-check the original model provenance; the current animated mesh is a **proxy**, not the original USDZ.
- [ ] Verify the GLB/Blender-to-FBX conversion (rig, >3 actions, materials, export metrics) on a Windows host with Blender.
- [ ] Compile `NARIS_W04Editor` C++ in the actual UE 5.7 installation and resolve any UHT/API errors.
- [ ] Run `tools/unreal/import_fiery_demon_runtime.py` through the Windows build script; validate the generated native `.uasset` / `.umap`, static environment, actor placement, collision, and material imports.
- [ ] Confirm in a fresh packaged log the **two** smoke markers: correct `LogLoad` and `NARIS_FIERY_DEMON_RUNTIME_READY`.
- [ ] PIE/combat test: aggro, pursuit, lock-on, two phases, wall-blocked impact, dodge/parry, death/save, post-death load, VFX/audio, normal and AR/EN HUD.
- [ ] Benchmark average, 1% low and frame-time stability vs 60 fps target; check crash and memory.
- [ ] Run a Windows Release Candidate build only after all blockers are clear. Never mark production approved before these gates.

## How to run (on the authorized development machine)

From a working copy containing the GLB source under `Assets\`, start:

```powershell
tools\windows\RUN_NARIS_FIERY_DEMON.cmd
```

The launcher calls `Invoke-NarisFieryDemonBuild.ps1`. It is designed to build and launch QA on the Windows workstation; it is **not** a downloadable prebuilt EXE. It reports `editor_map_saved`, `buildcookrun_pass`, and `process_alive_map_loaded_and_demon_actor_ready` *only if those steps execute and verify locally*.

**Current decision:** source/regression gates passed. **UE engine execution, playable combat, Windows package and Shipping remain NOT VERIFIED.**
