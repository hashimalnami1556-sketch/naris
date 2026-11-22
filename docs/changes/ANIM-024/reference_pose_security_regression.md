# ANIM-024 — reference-pose capture and editor-evidence regression (2026-11-21)

Scope: source-only read-only UE5.7 preflight. PR #110 remains DRAFT. Nothing under `unreal/NARIS_W04/Content`, the project `.uproject`, or any original user GLB has been modified by this change.

## Before / after (code evidence, NOT Unreal screenshots)

| Contract | Before | After |
| --- | --- | --- |
| Editor provenance | `validate_snapshot().engine_evidence` mirrored the forgeable JSON field `is_unreal_editor_capture`. | `engine_evidence=False` unconditionally on file-based and returned JSON reports; retain `claimed_editor_capture` solely as untrusted provenance. |
| Target skeleton capture | Bone names and parent hierarchy only. | For every discovered bone, capture both `reference_local_transform` (parent space) and `reference_global_transform` (model/skeleton space), each with numeric translation[3], quaternion rotation[4], scale3d[3]. |
| Data integrity | No validation of bone reference transforms. | Reject partial coverage, malformed fields, non-finite components, and zero quaternions. Old hierarchy-only snapshots remain accepted for *structural* validation only. |
| UE editor APIs | `SkeletonModifier.get_all_bone_names()` and `get_parent_name()`. | Additional documented read accessor `get_bone_transform(bone_name, global_=False)` with False and True. No commit/save/create methods. |

## TDD evidence
1. **RED:** add failing tests first, commit `57ef1db1eec8878110678d3ce0fd2def01927e1b`, [GitHub Actions run 44824178739](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44824178739) concluded FAILURE with prior code.
2. **Fix:** read-only implementation commit `88d56bc7f0d628134d946cc6d2685185579dafb3`.
3. **GREEN:** see latest `ANIM-024 Source Motion Coverage` workflow on PR #110; execution must pass before treating this source regression as closed. Unreal runtime not covered by this workflow.

## Remaining acceptance evidence
- Real UE 5.7 editor session and log; actual loaded `IKRig` / `MeshModelingToolset` / `PythonScriptPlugin`.
- Imported **production target** SkeletalMesh, correct bone/mesh reference pose and import units, manually signed-off seven semantic retarget chains. 18-joint source prototype is not the 87-bone production rig.
- IK Rig / IK Retargeter only after target review; actual Animation Sequences, ten required W04 Montages and Notifies, PIE, dedicated server+2 clients, Build Development, BuildCookRun, Project.* automation.
- Fixed Seed/1920x1080/quality UE before/after/diff, FPS, frame time, RAM, VRAM, package size and rollback attached before merge. **All runtime/perf/image gates are NOT RUN**; do not fabricate comparison screenshots.

## Known limitations
- JSON snapshots, even containing plausible transforms, are not cryptographic or independently verified editor evidence.
- Current v1 validation checks geometric data well-formedness, **not** animation quality, human anatomy, correct source/target scale, UE import settings, bind-pose fidelity, or network replay.
- UE 5.7 Python APIs are experimental; editor read capture must be tested on the user's actual installation, and `SkeletonModifier.set_skeletal_mesh` read effects observed.

**Status:** DRAFT / NO MERGE / production_ready=false.
**Rollback:** revert the test and tool changes on PR #110; no production `.uasset` replacement required.

Official references: [Epic SkeletonModifier UE5.7](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SkeletonModifier?application_version=5.7), [Epic Transform UE5.7](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/Transform?application_version=5.7).
