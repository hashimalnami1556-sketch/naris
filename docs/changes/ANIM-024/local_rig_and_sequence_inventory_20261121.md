# ANIM-024 — source-to-engine animation reconciliation (actual AsusRog assets, 2026-11-21)

**Nature:** read-only observed local Blender FBX/JSON and real UE5.7.4 AssetRegistry exports. No retargeter, montage authoring, artwork rewrite, production source import, network gameplay authority or screenshot approval is claimed.

## Local CHAR-001 review candidates

At `C:\dev\NARIS_CHAR001_20261107\RigSkinCandidateV6`:
- `AshWanderer_RigSkin_Review.blend`: 17,381,782 bytes.
- `SK_AshWanderer_Review.fbx`: 2,291,612 bytes, SHA256 `F6BC5FBC18EDA696F698FB996463AD8378C3C796A01C6775A70B2DDEFD6660C7`.
- `A_AshWanderer_QA_Motion.fbx`: 223,948 bytes; associated diagnostic motions **not production-approved combat**.
- Actual `rig-skin-review.json`: `status=REVIEW_CANDIDATE_CREATED`, `bone_names` array **18**, `production_approved=false`, `production_92_node_gate=OPEN`, `visual_deformation=PENDING_REVIEW`. Source SHA256 `4ccdb8a33231fc2c3a057c011e8775225ed49e5119ecbcb84ddefeac96129ac6` and unchanged source claims are in the report.
- **Consequently** this FBX is a separate *prototype review*, not the intended 87-bone Unreal production skeleton / 92-node advanced authoring skeleton. Do not import it over the 53-bone Ashen Vessel or infer a valid retarget pose.

## Real W04 AnimSequence inventory (UE AssetRegistry)

Actual runtime asset metadata captured in `C:\dev\NARIS_ANIM024_20261121\ue_asset_inventory_v2.json`; **78 loadable AnimSequences**, grouped by Skeleton pointer:

| Skeleton grouping | Sequences |
| --- | ---: |
| `SK_CelestialWolf_RIG_V3_Skeleton` | **50** |
| `SK_CelestialWolf_UNITS_V8_Skeleton` | **12** |
| `SK_AshenVessel_RIG_V3_Skeleton` | **9** |
| `SK_BoneBeast_RIG_V3_Skeleton` | **7** |

Ashen Vessel's nine existing sequence names observed inside engine include `AN_Ashen_Idle`, `AN_Ashen_Walk`, `AN_Ashen_Run`, `AN_Ashen_Attack_Light`, `AN_Ashen_Attack_Heavy`, `AN_Ashen_Dodge`, `AN_Ashen_Parry`, `AN_Ashen_HitReact`, `AN_Ashen_Resonance`. Durations include Idle **0.9667s**, Walk **0.7667s**, Run **0.5s**, LightAttack **0.5s**, HeavyAttack **0.7s**, Dodge **0.7s**, Parry **0.5667s**.

### What this does and does not resolve

- This refutes the overbroad claim that there are no real animation sequences on the user's UE installation; **they exist and load**. It does not prove the motion was authored, licensed, aesthetically acceptable, gameplay-correct or retargeted to the intended production skeleton.
- Existing four Wolf V9 Montages and 12 V8-skeleton AnimSequences may share target Skeleton where observed, but the **10 exact W04 manifest Montage objects remain 0/10 loadable**. A source AnimSequence is **not** a playable, correctly notified, attack-authority-aware AnimMontage by name alone.
- Do not auto-create/retarget production IK or replace source assets from these prototypes; preserve the ability to import the true advanced rig when ready.
- **Next blocker** is an actual production target skeletal mesh with reviewed reference pose, correct hierarchy/weights and approved original gameplay clips. Per change policy, only then create source/target IK Rigs, Retargeter and reviewed Montages, running real before/after, BuildCookRun, network combat replication and measured graphics profiling.

**State:** evidence reconnaissance advanced; **ANIM-024 remains DRAFT / DO NOT MERGE**. Rollback: read-only inventory did not modify game assets.
