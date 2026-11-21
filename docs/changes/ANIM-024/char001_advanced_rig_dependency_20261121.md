# ANIM-024 dependency correction: 87-bone CHAR-001 guide exists, but production skin is rejected

**Read-only verified 2026-11-21 on AsusRog**. Corrects the overbroad phrase "no 87-bone rig exists": an advanced rig guide and multiple Blender skin candidates **DO exist locally**, but **none is approved as a deployed game character**.

## Original files and evidenced outcomes

Local master evidence lives in `C:\dev\NARIS_CHAR001_20261121` and `CHAR001_QA_HANDOFF\Reports`. These files are NOT in the `hashimalnami1556-sketch/naris` GitHub PR and should not be invented as remote assets.

- **G1B fit guide**: `AshWanderer_G1B_87_FITGUIDE_UNBOUND.blend`, **87 named bones, 83 deform, 4 helper, five socket guides**, 32,373 source body/weapon vertices; `status=PASS_STRUCTURE_NOT_SKIN`, **UNBOUND** and thus unusable for a production runtime SkeletalMesh. SHA256 `9d201128fdb410e578cd3a5f7098666d67d19bd14d99c24935f8a451d0f5b5d6` from the local report; no in-engine rig import/retarget claim.
- **G1C 87-bone skin**: `AshWanderer_G1C_87_SKIN_CANDIDATE.blend`, 31,257 body vertices, 83 possible deform bones but **only 17 bone groups received imported source weights**; stress pose evaluated on 78,831 edges, **923 edges stretched by >2x**, max local edge ratio **57.53x**. `g1c_87_skin_report.json` states `SKIN_BIND_REVIEW_ONLY`, and `g1c_stress_qa.json` states `DIAGNOSTIC_POSE_ONLY_NO_ARTIST_APPROVAL`. SHA256 `b6e12ff4dbd41a3eb6389de7beffd3e294a706e491de45cbc14cea36787ee4e1`.
- **G1D smoothing candidate**: localized smoothing reduced >2x stress edges to **848** in its best trial, but max ratio still **15.90x**; `production_approved=false`, `quality_gate=BLOCKED_PENDING_VISUAL_AND_UNREAL`, with potential unwanted cloth/armor softening.
- **G1F foot-IK guide**: local `AshWanderer_G1F_87_FOOT_IK_REVIEW.blend`, IK target initial geometric error ~1 micrometer. `ground_trace=NOT_IMPLEMENTED`, `foot_lock=CONTROL_ONLY`, `unreal_import=NOT_ATTEMPTED`, `production_approved=false`. A control object/foot target is not a validated run-time foot planting system.
- **G1L latest evaluated constrained-weld candidate**: `AshWanderer_G1L_WELD_CONSTRAINED_QA.blend`, SHA256 `e2c048ae73f542637e55ba37a139def59a72eb5f96a011bf349ea4e3f1041892`, actual Blender read-only numerical pre/post validation status `ACTUAL_BLENDER_EVALUATION_PASS__NOT_PRODUCTION`. Mesh vertex positions and polygon topology unchanged. **17 active weighted bones**; severe over2x edges across seven diagnostic poses decreased in a later heuristic trial but remain **905 (stress), 1704 (attack_left), 1070 (attack_right), 601 (step_left), 277 (step_right), 1121 (turn), 1408 (guard)**. The maximum edge expansion on the attack_left pose still **177.07x**. `production_approved=false`. This is not production gameplay-ready simply because some counts improved.
- **V8 body/sword separation**: `SK_AshWanderer_V8_Body.fbx`, `SM_AshWanderer_V8_Sword.fbx` were imported into an **other isolated UE5.7 project**, not NARIS_W04: `/Game/NARIS/CharacterReview/CHAR001_20261107/RigSkinV8`. 19 Unreal reference nodes including one wrapper, versus 18 source joints. Neither V8 nor G1L was bound to the current W04 hero pawn. `unreal_v8_apply.json` explicitly states `production_g0=OPEN`, `production_g1=NOT_APPROVED`, `runtime_binding=NOT_CHANGED` and `visual_acceptance=NOT_REVIEWED`.

## Integration gate (hard FAIL)

Do NOT overwrite the live AshenVessel V3 53-bone skeleton or import G1L into game maps. The advanced 87-bone skeleton is only a local *guide/candidate* until:
1. Complete anatomically sound weight transfer for actual body zones and joints, inspect fingers/twist/cape/armor; no severe geometric stretch and no mesh detachment in multi-pose quality review
2. Validate anatomical proportions, source scale, skin influences, retarget root, bind/reference transforms, sword socket in **the actual W04 Unreal project** and record genuine screenshots from the same fixed camera
3. Approve original Idle/Walk/Run/Attack/etc source sequences plus matching 87-bone IK Retargeter and animation blueprint
4. Test PIE actual movement, foot planting, server + two clients authoritative motion/combat, same-Seed screenshot diff and numeric representative FPS

**ANIM-024 status:** asset exists as unapproved advanced 87-bone design, **production character still missing/rejected**; target import, retarget, gameplay, merge and release remain **BLOCKED**. Do not claim 87-bone gameplay integration until the preceding steps are measured. Original user-owned local files were only read; no destructive operations.

Source trace: local `CHAR001_QA_HANDOFF\Reports\report.md`, `g1c_stress_qa.json`, `g1d_local_weight_qa.json`, `g1f_foot_ik_setup.json`, `g1l_actual_blender_validation.json`, `g1l_weld_constrained_report.json`, `unreal_v8_apply.json`. Technical reference: [Epic Skeletal Meshes](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-assets-in-unreal-engine), [Epic IK Rig retargeting](https://dev.epicgames.com/documentation/en-us/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine).
