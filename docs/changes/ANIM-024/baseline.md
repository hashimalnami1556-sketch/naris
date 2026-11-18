# ANIM-024 — Source animation coverage baseline
Date: 2026-11-18. Parent branch: feature/CHAR-023-rigid-weapon-review. Scope: source-only, no UE changes.

## Actual original file audit
Four user-provided GLB assets inspected by parsing glTF JSON chunks:
- CHAR-022 skin-fixed hero, SHA256 a9389d433d31886c1d4273e6acda0950ca6657fac20338063b9bb643ca95fdd9: 1 skin, 1 clip `A_Character1_Idle`, 1 rotation channel targeting `chest`. Walk, Run, Attack, Dodge, Block, Death absent.
- `Character1_NARIS_Rigged_Prototype.glb`: 1 skin, 1 clip `A_Character1_Idle`, 1 rotation channel targeting `chest`.
- `Character 1.glb`: no skin and no animation.
- `Character 3.glb`: no skin and no animation.

The audit requires named clips Idle, Walk, Run, Attack, Dodge, Block, Death. Name presence alone is a **minimum content check, not proof** of skeletal coverage, retargeting, root motion, foot IK or runtime playability. All four sources fail minimum coverage. No animation has been generated or retargeted. Do not silently create placeholder clips or mark ready.

## TDD and evidence
Local RED: ModuleNotFoundError: anim024_audit before implementation. GREEN: 5/5 unit tests including the real user-supplied CHAR-022 GLB, with pinned source. For GitHub CI the real-asset test must skip explicitly if `NARIS_ANIM024_SOURCE` is not set; original GLB remains external, not checked in. Source-only JSON evidence and Python reproducibility script provided in chat handoff.

## Next actual production tasks
1. Verify UE5.7 character Skeleton, bone hierarchy, bind pose, import scale and rotation; compare with target Manny/Quinn if retargeting to UE assets.
2. Acquire/licensed original source locomotion and combat animation clips; validate names, source rigs, licensing and original style. Do not invent gameplay animations.
3. Create IK Rig source/target and IK Retargeter in UE; map pelvis, spine, arms, legs and head; validate retarget root and foot contacts.
4. Author animation blueprint / locomotion BlendSpace and Montages with root-motion policy, Foot IK, combat cancel windows and replicated gameplay.
5. Run UE actual before/after 1920x1080, BuildCookRun, automation Project.*, server+2 clients, FPS and memory; no merge until green.

## Gate status
- Offline file inventory and missing-clip detection: PASS.
- UE import/retarget/animation preview/PIE: NOT_RUN.
- Combat/replication/build/performance: NOT_RUN.
- Release and merge: BLOCKED.

Rollback: revert documentation and audit utility; original GLB and UE project remain untouched.
