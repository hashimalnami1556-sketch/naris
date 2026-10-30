# CHAR-001-G0 — Ash Wanderer Skeleton Contract

## Scope
Lock the production skeleton contract before Advanced Rig construction. Target: 92 production deform/export bones.

## Decisions
- Production runtime: Unreal Engine 5.7.
- Root contract: one root at origin, scale 1.0, pelvis directly below root.
- Coordinate contract: Unreal Z-up / X-forward / centimeters. Blender authoring must be exported with explicit conversion rather than arbitrary object transforms.
- Deform and Twist bones may affect skin. Helper bones must not affect skin unless promoted to a documented runtime deform role.
- Control Rig is a separate authoring layer and MUST NOT be exported in GLB/game skeleton.
- Attachment markers/sockets do not consume skin weights.
- Maximum skin influences: 4 per vertex.

## G0 Tasks
- T1: names, hierarchy, axes documented.
- T2: every bone classified DEFORM/TWIST/HELPER/ATTACHMENT/CONTROL.
- T3: root/pelvis/axis contract + UE import smoke.
- T4: GLTF export audit: no duplicates, unused controls, or accidental Control Rig export.
- T5: 12 structural tests in CHAR-001-G0-TESTS.md.

## Gate
G1 is BLOCKED until T1–T5 have evidence. Current status: G0_OPEN_ANATOMICAL_FIT_AND_ENGINE_EVIDENCE_PENDING.

Recovered source hierarchy and remaining anatomical-fit requirements: [CHAR-001 checklist](../../characters/char-001/execution-checklist.md). The 92 count includes the motion root; it does not imply all nodes must carry skin weights. Source specification is not yet fitted or approved.
