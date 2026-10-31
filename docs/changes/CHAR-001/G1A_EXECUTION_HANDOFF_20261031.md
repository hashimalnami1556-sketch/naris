# CHAR-001 / G1-A — execution handoff (blocked, 2026-10-31)

**Status:** G1-A reference implementation prepared offline. **No Blender `.blend` has been generated or validated on the authorized workstation.** No Unreal/PIE/Shipping execution has occurred. Production gate remains **BLOCKED**.

## Source inspection evidence
- Source asset: `naris_3d_ash_wanderer.glb`.
- SHA-256: `06c07d245c3830bfac6b473b8ca24852171bd3185fb5e1e902b387d1ed02ecdf`.
- One source glTF mesh; 6,520 vertices; 4,131 triangles; **0 skins**.
- Source glTF uses Y-up; offline world-space height = **0.994140625** units.
- A provisional uniform scale factor of **1.8106090373** brings the working COPY to 1.80m; exact anatomical landmarks still require review.
- Source original remains unchanged. No transforms are applied blindly to a skinned mesh.

## Contract collision found — DO NOT IGNORE
The recovered `docs/characters/char-001/ash-wanderer-source-spec-v1.json` is a **92-bone unfitted design**, with 75 deform + 16 twist + 1 root, five spine segments, three neck segments and eyes. Its source uses `_L/_R` naming and a 12-bone cape.

The latest owner-approved work specification in chat is instead:
- **92 authoring entities = 87 runtime bones + 5 Unreal sockets**;
- **87 runtime bones = 83 deform + 4 helpers**;
- G1-A central axis = **11 bones**: root → pelvis → spine_01..04 → chest → neck_01..02 → head → jaw;
- nondeform root; pelvis/jaw disconnected from parent tail; no Skin/IK/Control Rig/animation at G1-A.

These are **not equivalent hierarchies**. Preserve the recovered 92-bone JSON byte-for-byte; never silently substitute or rename it. Reconcile anatomy, naming, character identity and rest matrices before signing G0.

## Offline deliverable
`Ash_Wanderer_CHAR001_G1A_Execution_v3.zip` prepared in the current ChatGPT conversation; ZIP SHA-256:
`4582dfae3f08130b7afc395ef93463825b9d7ebbd80c15ba8446f100c1179450`.

Package contains source GLB; approved 87-bone target JSON; original 92-bone unfitted source; a non-destructive Blender G1-A builder; a real-`.blend` structural validator; Windows runner; source baseline; front/side *offline* geometry overlay; seven passing offline unit tests. The ZIP is **not** a GitHub-hosted artifact and is **not** evidence of a saved `.blend`.

## Required before G1-A PASS
1. Resolve G0 schema conflict; record owner/technical signoff and accepted spec hash.
2. On Windows with Blender 4.x, run `Scripts/Run_CHAR001_G1A.ps1` from the extracted package.
3. Confirm actual `02_Rig/SK_AshWanderer_Advanced_G1A.blend` and Blender structural QA output; keep before baseline.
4. Capture Front Orthographic, Right Orthographic, Outliner and Bone Axes from the actual Blender session, 1920×1080.
5. Correct pelvis/spine/chest/neck/head/jaw joint placement from the Mesh and record acceptance.
6. Keep G1-B blocked; Unreal smoke remains a later evidence gate.

## Current test truth
- Offline contract tests: **7/7 PASS**.
- ZIP integrity: **PASS**.
- Blender operator execution: **NOT RUN** (Blender not installed in chat container).
- Visual anatomical validation: **PENDING**.
- Unreal 5.7 import: **PENDING**.
- Performance delta: **NOT MEASURED**.

Rollback: discard this *draft documentation branch*; it makes no production asset changes. Tracks #86.
