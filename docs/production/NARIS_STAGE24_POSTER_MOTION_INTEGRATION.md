# NARIS Stage 24 — Poster Motion Integration (2026-10-26)

## Scope and verified state
The user-approved 5x5 character/motion poster is the **art-direction and animation coverage reference**, not proof of playable character assets. This change records a safe integration gate for Unreal Engine 5.7 / W04.

- Poster roster: **25** characters and creatures, **150** named motion slots (six per character).
- Stage23 source package: **10 GLB prototype models** with procedural animation studies; **120 poster slots** are **not** marked as GLB procedural studies in that package's exact coverage table.
- The available GLBs do not establish advanced anatomical rigs, production-quality skin deformation or motion-capture animations.
- Final imports, Montage Notifies, Foot IK, inverse kinematics, root motion, game performance and PIE tests remain **NOT RUN**.
- Do not mark design-only slots or prototype files as production-ready in `data/MASTER_ASSET_REGISTRY.json`.

## Repository and import policy
- Target: `unreal/NARIS_W04/NARIS_W04.uproject` (EngineAssociation 5.7).
- Import experiments into `/Game/NARIS/Prototypes/Stage24/`; never overwrite production mesh, skeleton or animations.
- Stage24 package contains an offline-validating registry, the ten original stage23 animated prototypes and an optional Unreal Editor Python import helper.
- Run the offline validator first, then import manually or via editor script; inspect imported asset classes and skeleton bindings and record real Unreal execution results.

## Remaining gates in order
1. Match all poster characters against registered 3D models and author missing meshes.
2. Model-specific advanced rigs, UV/PBR skin weights and vertex-deformation QA.
3. Distinct walk/run/combat/skills/death animation authoring, contact and blend tests.
4. Unreal import, skeleton/retarget checks, AnimBlueprint/Montage wiring and damage notifies.
5. Foot IK + root motion consistency, AI, PIE smoke test, shipping build and profiling.

## Offline evidence
The delivered NARIS_STAGE24_REPO_INTEGRATION.zip was validated locally: 10 readable GLB structures, 150 registry rows, checksum matches and an intact ZIP. **This GitHub commit does not upload the binary GLBs**, which remain in the deliverable archive; use Git LFS and reviewed provenance before uploading art assets.
