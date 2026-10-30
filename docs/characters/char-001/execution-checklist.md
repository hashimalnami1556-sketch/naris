# CHAR-001 — Ash Wanderer production gate

Owner: project owner. Executor: Codex. Date: 2026-10-30.
Tracking: https://github.com/hashimalnami1556-sketch/naris/issues/86
Status: G0 DRAFT; G1–G6 NOT STARTED. No production approval.

## Scope and freeze

Ash Wanderer is P0. Freeze new rigs/expansion for Demon, Bone Hound, Aether Serpent and Dragon until Ash closes G0–G6 including Unreal animation tests. Existing assets remain intact. NET-001 is independent and must not block character specification work. HUD/audio/save expansion stays P2; existing functionality is preserved. Multiplayer readiness requires both CHAR-001-G6 and NET-001.

This change adds specifications only, with a textual Git diff. It does not alter a model, game scene or runtime. The owner's engine before/after capture gate still applies before subsequent rig/game implementation; no synthetic screenshots are supplied for this document.

## G0 — exact draft hierarchy and export boundary

SUPERSEDED DRAFT: the companion CSV is retained for historical comparison only; do not build from it. The recovered source spec `ash-wanderer-source-spec-v1.json` is now the reference for review. The earlier draft explicitly enumerates 92 exported nodes: 14 central/root/head, 48 arms/hands, 22 legs/feet and 8 garment deform bones. Root is an exported motion node and may have no skin influence. Twist/corrective/garment nodes must demonstrably deform intended regions; counting an unused node is not acceptance.

This allocation is a design candidate, not an observation of the supplied GLB. Garment chains and correctives require topology review before approval; change the allocation rather than manufacture weights solely to reach 92. Confirm whether the source identity Ash Wanderer maps to the canonical Ashen Vessel registry entry; preserve IDs and do not silently rename or promote either asset.

Blender scene convention: meters, Z up, character faces -Y; bone local +Y runs head to tail. Bone roll uses a mirrored anatomical local-Z reference. Exact rest matrices, joint locations and per-bone roll angles remain OPEN until geometry inspection; do not fabricate them in a name table. Unreal conversion: centimeters, +X forward, +Z up. glTF uses its standard right-handed Y-up scene convention. Apply coordinate conversion once and verify basis markers, scale and bind matrices by round-trip import; never use negative object scale to mirror the exported rig.

The historical CSV is NOT the current game export allowlist. Derive the reviewed allowlist from the recovered source JSON after resolving its role/axis/landmark mapping. Control rig objects, IK targets, poles, constraints and mechanism bones stay in the authoring file and are excluded from game skins/nodes. Use non-exported controls for hand/foot IK, heel roll, toe pivot, knee poles and twist drivers. Weapon grip is an Unreal socket on hand_r, not an extra counted bone. Do not impose a 19-node glTF target: exported deform nodes plus necessary mesh/scene nodes are allowed; unrelated controls/cameras/lights are excluded. Do not claim UE mannequin naming or automatic retarget compatibility; G5 must establish the mapping.

- [ ] Confirm asset identity, mesh provenance, handedness, proportions and garment topology.
- [ ] Review every CSV name, parent, role, joint location, rest matrix and mirrored roll.
- [ ] Pass unique naming, one-root, parent existence and acyclic hierarchy checks.
- [ ] Record approver/date and accepted specification hash. No G1 promotion before G0 closes.

## Ordered task checklist and Definition of Done

| Task | Work | Definition of Done / retained evidence |
|---|---|---|
| CHAR-001-G0 | Freeze skeleton spec | Explicit accepted 92-node hierarchy, axes/rest transforms, export filter, naming checks and reviewed topology allocation |
| CHAR-001-G1 | Build authoring rig | Source blend/scene + export; hand/foot IK, twist drivers and root/pelvis separation; all 12 structural checks below pass on actual files |
| CHAR-001-G2 | Paint weights | At most four positive exported-bone influences per vertex; normalized sums within 1e-4; no unweighted vertices; T/A poses, squat, arm raise and torso twist inspected with weights and before/after views |
| CHAR-001-G3 | Solve foot IK/twist | Flat, ramp and stair tests; locked-foot world-space drift <= 0.01 m in every plant window; toe pivot/ankle roll; no knee flip or visual pop; clips and measured contact trajectories |
| CHAR-001-G4 | Author motion set | idle/walk/run/attack/defend/hit/death; specify actual authored m/s and foot contact windows before evaluating; seamless cyclic clips only where appropriate (not death/one-shot attacks); transitions and attack windows reviewed |
| CHAR-001-G5 | Integrate Unreal | Real Skeletal Mesh, Skeleton, Physics Asset, Anim Blueprint and Blend Space; third-person map; retarget chain/root mapping and scale verified; G2–G4 checks repeated in engine; no clear clipping |
| CHAR-001-G6 | Build and profile | Windows Development package and playtest; joint deformation reviewed at gameplay camera distances; measured animation CPU/GPU/LOD cost, RAM and package size meet canonical docs/perf budgets; reports, commit, PR and build link retained |

### G1 — twelve structural checks (not executed)

1. Exactly 92 exported allowlisted skeleton nodes; controls excluded.
2. Unique valid bone names and no case-fold collisions.
3. One root; every other parent exists; no cycles/disconnected branches.
4. All rest transforms finite and invertible.
5. Every bone has a nonzero head-to-tail length at project scale.
6. Mesh/armature object scale is applied (1,1,1), with no reflection or shear.
7. Measured stature and centimeter/meter round-trip agree.
8. Anatomical axes and mirrored bone roll match reviewed rest transforms.
9. Root and pelvis are separate; moving root carries the whole character.
10. Constraints/drivers/IK solve without dependency cycles; controls do not leak into export.
11. Bind/inverse-bind matrices preserve rest mesh after export/reimport within declared numeric tolerance (initial review target 0.1 mm).
12. All intended twist/corrective/garment drivers evaluate and survive baking; no unsupported runtime constraint dependency.

### Visual and runtime acceptance

Shoulder volume, elbow candy-wrapper, knee collapse and hip twist are visual failures even if numerical checks pass. Capture neutral pose and identical stress views, including >90-degree shoulder/hip poses where anatomically applicable. Left/right, front/back and camera-near views must be reviewed. No geometry-volume threshold is invented here; retain visual review and resolve visible failures.

For every motion test, record units, contact windows, sample rate, root-motion/in-place mode, playback speed, slope/stair geometry, seed, camera, resolution and hardware. Measure foot drift from the start-of-plant anchor through the plant window; do not compare only first/last frames. Lock requested engine capture configuration before taking before/after frames. Performance targets come from canonical production/performance documents; target values are not measurements.

## Handoff and rollback

Current evidence: specification CSV only. No Blender build, weight painting, Foot IK, motion authoring, Unreal import or package execution is claimed. Existing 30-degree stress coverage and bone-count checks cannot close the production gates. G0 remains open pending asset-specific rest transforms and review.

Next action: inspect the actual Ash source mesh/armature and reconcile the draft hierarchy, then capture the required implementation baseline before G1. Rollback: revert this specification-only commit; existing assets/runtime remain untouched. After Ash passes: Demon (106, share humanoid structure only after proven compatibility), Bone Hound (separate quadruped), Serpent (separate chain), Dragon (independent 146, after pipeline stability).

## Source recovered — 2026-10-30

Recovered the actual Advanced Organic Rig v1 archive, Library ID libfile_59072242fa748191b1a9f8189f9cbaf0. The original Ash JSON is retained byte-for-byte in ash-wanderer-source-spec-v1.json; hashes and comparison against the superseded CSV are in source-reconciliation.json. Source count: 14 central/head + 48 arms/hands + 18 legs/feet + 12 cape = 92. Roles: motion_root 1, deform 75, twist_deform 16. Naming uses uppercase L/R suffixes and source twist naming; do not silently rename it to the previous CSV convention.

Fresh checks passed on the recovered source: count, exact/casefold unique names, single root, existing parents and acyclic hierarchy. No monster rig was built or modified.

V3 tool tests: 10 synthetic regression tests pass, but its JSON input is not this source schema. It requires head/tail/export fields, different roles and explicit axes, while source v1 intentionally keeps landmarks external. Do not run the builder against a fabricated schema conversion or interpret schema rejection as a failed rig. Review the role/export mapping, mesh identity, all anatomical landmarks, roll/rest matrices and twist source/target drivers before closing G0. The original archive marks DESIGN_CONTRACT_NOT_FITTED, REQUIRED landmarks, NOT_CREATED weights and NOT_IMPLEMENTED drivers.

The available Character1 prototype was independently audited: 19 nodes, 18 skin joints, one mesh and one animation, no duplicate joint names or out-of-range joint indices. This is not proof that it is the canonical Ash mesh. No revised skin, IK, Unreal import or new engine capture was produced. G0 remains OPEN; G1 remains NOT_STARTED.
