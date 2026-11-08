# CHAR-001-R7 — Offline action continuity repair & exact rig contract

**Status:** NON-PRODUCTION / DRAFT / DO NOT MERGE until Blender and Unreal gates close.
Issue: #86. Source assets and project main remain unchanged.

## Why

The R6 authored animation used a pelvis keyframe from the R4 combat idle at **0.867 m** in the place of the unanimated node-local position **0.930 m**. Entering/exiting guard jumped the entire body by **63 mm**. Hit reacted too far below the floor, and the original death swung the sword into the ground. Separately, the existing Blender weight gate incorrectly counted **92 deforming bones** where the recovered source spec defines **92 exported nodes including one non-deforming motion root**, i.e. **91 deforming bones**.

## What changed on this isolated branch

- Added `tools/blender/naris_rig_spec_contract.py`: structural validation of bone names, casefold uniqueness, exact hierarchy, exact deform flags, and allowed non-deforming authoring controls. Structural checks NEVER claim rest matrices, skin quality, authored motion, or Unreal validation.
- Connected `tools/blender/naris_advanced_rig_weight_gate.py` to the source-spec contract only for Ash Wanderer, preserving separate (unverified) legacy checks for unrelated creature rigs.
- Added `tests/test_naris_rig_spec_contract.py`: 9 deterministic synthetic regression cases plus one source-spec integration case.
- Added isolated GitHub Actions contract check. It does NOT replace project build, net, or performance CI.
- Local R7 GLB is a **test artifact only**, not a game asset in this PR. It retains original seven clips unchanged and replaces the five R6 reference actions with five R7 reference actions. Invalid R6 actions are not included in the R7 animation list.

## Offline comparison, 121 samples per clip

| Check | R6 | R7 | Meaning |
|---|---:|---:|---|
| Guard Enter -> Hold pop | 63 mm | 0 mm | Transition continuity fixed at evaluated boundary |
| Guard Hold -> Exit pop | 63 mm | 0 mm | Transition continuity fixed |
| Hit reaction lowest body geometry | -110 mm | -48 mm | Meets provisional -50 mm triage, but still near floor |
| Death body lowest geometry | -224 mm | +18 mm | The R7 **kneel** is a temporary safe reference, NOT a complete death sequence |
| Death sword lowest geometry | -811 mm | +298 mm | No sword-under-floor samples in flat CPU preview |
| Death max edges stretched >2x | 4.235% | 1.585% | Structural triage only, not visual approval |

Every result is from offline flat-ground CPU linear skinning with approximate 30-joint rig, not Unreal. These figures do not prove realistic motion or net correctness.

## Tests

Local `pytest -q tests/test_r7.py repo_tests/test_rig_spec_contract.py`: **18 passed** (9 GLB artifact regressions + 9 contract unit tests). The repository's additional real source-spec integration test awaits its own CI run. The Blender script itself has not been executed by Blender.

## Artifacts (separately delivered, not vendorized)

- GLB: `AshWanderer_R7_FlatGround_Reference_ONLY.glb`
- Evidence: `QA_R7.json`, `evidence/before_after_R6_R7_OFFLINE.png`, `evidence/diff_R6_R7_OFFLINE.png`, `evidence/R6_R7_DEATH_OFFLINE_REVIEW.gif`.
- Six vector SVG views: roadmap, rig contract, animation state graph, measured QA, gate matrix, Unreal handoff.
- Authoring, verification, test scripts and SHA256 manifest are in the delivered local QA package.

## Hard blockers

1. Source JSON is a **design contract not yet anatomically fitted**. No valid production 92-bone deform rig, inverse-bind/rest placement, per-vertex weights, or Blender controls exist for R7.
2. R7 `Death_Kneel` is only a stopgap; credible defeat should be mocap/retargeted or driven by correctly configured Unreal physics, with authoritative multiplayer death.
3. Real-time Foot IK against slopes, stairs, and collisions is unimplemented.
4. Required consistent UE 5.7 screenshots, build, cook, automation Project.*, server+two clients, and performance readings were **not executed**. No Windows/UE computer is paired.
5. Branch is source-only: no LFS GLB uploaded, no materials/animation blueprint changed, and no production mesh replaced.

## Rollback / safe adoption

Do not merge this draft until blockers are resolved. To abandon: close the draft PR and delete the `feature/CHAR-001-R7` branch; `main` and game assets remain untouched. For future actual GLB adoption, use Git LFS and preserve original source and license/provenance records. Never import failed R6 actions.

## Further engineering references

- Source-of-truth: `docs/characters/char-001/ash-wanderer-source-spec-v1.json`
- Unreal Interchange: https://dev.epicgames.com/documentation/unreal-engine/importing-assets-using-interchange-in-unreal-engine
- IK Retargeter: https://dev.epicgames.com/documentation/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine
- glTF 2.0: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
