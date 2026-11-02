# CHAR-001 / G0 — Approved numeric contract (v2)

## Owner's latest approved target
- **92 authoring entities** = **87 runtime skeleton bones** + **5 Unreal sockets**.
- **87 runtime bones** = **83 skin-affecting** (67 primary + 16 twist) + **4 non-deform helpers**.
- Helpers: `root`, `cape_root`, `heel.L`, `heel.R` (`use_deform=False`).
- Sockets: `weapon_r→hand.R`, `weapon_l→hand.L`, `head_ui→head`, `shoulder_armor.L→clavicle.L`, `shoulder_armor.R→clavicle.R`.
- Source GLB: SHA-256 `06c07d245c3830bfac6b473b8ca24852171bd3185fb5e1e902b387d1ed02ecdf`, **0 skins**.
- **G1-A only** = 11 central bones, `root` non-deform, `pelvis` and `jaw` disconnected from parent's tail.
- Max 4 skin influences/vertex applies at G2, not G0.

## Provenance conflict, not a license to silently overwrite
The original recovered `docs/characters/char-001/ash-wanderer-source-spec-v1.json`
specifies a different **unfitted** 92-bone rig, including additional spine/neck/face and cape nodes.
Preserve that legacy source unchanged; **do not claim these two designs are identical**.
The owner-approved runtime budget is v2; fitting/naming/landmarks and technical signoff are pending.

## Gate boundaries
**G0**: numeric classification, hierarchy design, source provenance, coordinates and export policy.
**G1-A**: build and validate actual 11-bone central Armature in Blender, without Skin or Animation.
**G1-G**: verify all 87 runtime bones (83 deform, 4 helpers), hierarchy, roll, symmetry, lengths and GLB structural export.
**G2**: weights / normalization / 4 influences / visual deformation.
**G3/G4**: Foot IK, twist, gait, combat and other behavioral QA.
**G5**: Unreal import, five sockets, Physics Asset and AnimBP.

The original requirement to *complete a full 87-bone Unreal import before building G1* would be circular.
G0 records the **intended** export contract. Actual Unreal import evidence belongs to G5.
No runtime, visual or UE gate is marked PASS by static design checks.

## Status
Numeric specification: **OWNER_APPROVED**.
Source-specific anatomical joint/rest fitting: **PENDING**.
G1-A Blender execution: **PENDING**.
Unreal 5.7: **PENDING**.
G1-B: **BLOCKED**.
