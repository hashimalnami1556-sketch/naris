# ANIM-024 — actual project readiness and target IK preflight

**Date:** 2026-11-19. **EngineAssociation:** UE 5.7. **Change:** read-only tooling and reports only; no `.uasset` created and no original GLB edited.

## Verified sources
- Live GitHub source tree: 907 entries in this branch snapshot. **No target IK Rig / IK Retargeter `.uasset` files** in the checked-in tree.
- `unreal/NARIS_W04/Content/NARIS/W04/Animation/W04_AnimationBindings.json` enumerates **10 expected AnimMontages** for the hero, Celestial Wolf and Bone Beast. **0/10 expected `.uasset` paths** are present in the **checked-in repository tree**. These may exist on a user's local Unreal machine and not be committed; do not assert local absence.
- `unreal/NARIS_W04/NARIS_W04.uproject`: `PythonScriptPlugin` enabled; `IKRig` and `MeshModelingToolset` are **not explicitly listed as enabled**. That is a project-file finding, NOT proof the runtime plugins are disabled. Epic's Unreal Python 5.7 API defines `IKRigController`, `IKRigDefinitionFactory` and `SkeletonModifier`; actual editor import and availability remain unverified.

## New safeguards and implementation
- `tools/assetforge/anim024_target_preflight.py`: read-only capture of an **actual imported target SkeletalMesh** using `SkeletonModifier` within UE 5.7; never calls `commit_skeleton_to_skeletal_mesh` or any asset save/create API. Outside Unreal, validates a supplied capture snapshot and requires **seven explicitly supplied target chain pairs**. Validates unique bone names, one root, no cycles, target path in /Game, chain endpoints and ancestry, Root → pelvis / Spine boundary agreement. Does NOT infer Manny/Quinn target names and does NOT create a Retargeter. Refuses overwriting any output JSON.
- Important truth-in-evidence regression: an arbitrary JSON can claim `is_unreal_editor_capture=true`. The review now ALWAYS sets `verified_in_engine=false` for JSON analysis and records the flag separately as `reported_editor_capture`. Only a separately observed real editor session and its logs can prove runtime execution.
- `tools/assetforge/anim024_repo_readiness.py`: checks the W04 manifest's exact `.uasset` file paths in the supplied local Content directory. Absence is an outstanding source-control/content gap; presence alone does NOT validate the Montage class, Notifies, playable range or BuildCookRun.
- Project source audit written as `target_and_montage_repo_preflight.json`. No `.uproject` modifications have been made, so actual plugin activation needs local editor verification.
- CI now compiles/checks target/montage validators. TDD RED was reproduced for missing target-validation module and fake editor-claim regression. GREEN [GitHub run 44444969246](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44444969246) ran **66 tests**; **64 passed**, **2 skipped** because original GLBs are excluded from source checkout.

## How to use when UE5.7 with actual imported target becomes available

1. Confirm `IKRig`, `PythonScriptPlugin` and `MeshModelingToolset` classes actually load in Editor; do not blindly edit plugin settings from a guessed environment.
2. Select an **existing imported SkeletalMesh target** and copy its full object path, e.g. `/Game/Characters/Target/SK_Target.SK_Target` (example only, not an actual NARIS file).
3. From **inside UE Editor Python** run `anim024_target_preflight.py --uproject <project.uproject> --capture-unreal --mesh-asset <actual object path> --output <new report.json>`. This reads the target skeleton and writes JSON only, without writing any Unreal assets.
4. Review actual bone names and parents. Write a **manual** mapping JSON with schema `naris.anim024.manual-retarget-map.v1`, seven chains `Root`, `Spine`, `Head`, `LeftArm`, `RightArm`, `LeftLeg`, `RightLeg`, each with start/end target bone names and target pelvis/root chain alignment; do not guess target names from source.
5. Review actual skeleton translation/scale and target retarget pose visually. Only once a real target IK Rig and a verified source IK Rig exist should a separate, explicitly approved IK Retargeter build be considered.
6. Validate gameplay Animation Blueprint, real montages/notifies, sword hand attach, Foot IK, Build Development + BuildCookRun, Project.* automation, dedicated server + 2 clients, fixed 1920×1080 before/after screenshot/diff and FPS/RAM.

**Gates remain BLOCKED:** target imported SkeletalMesh not available in current environment; target IK Rig/IK Retargeter assets not created; original production motion clips absent from GitHub; no UE editor or multiplayer tests. Current change is **draft / DO NOT MERGE**.

## References (Epic Games UE 5.7 official)
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/IKRigController?application_version=5.7
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/IKRigDefinitionFactory?application_version=5.7
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SkeletonModifier?application_version=5.7
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/IKRetargeterController?application_version=5.7

**Rollback:** revert ANIM-024 target preflight source/test/docs changes; original project Content, skin, and materials are unaffected.
