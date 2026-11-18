# CHAR-023 — Rigid weapon candidate from original hero geometry
Date: 2026-11-18 | UE association: 5.7 | Branch parent: feature/CHAR-022-skin-binding @ e1b4fbf214286431db590c6fff7b8661d6cee849

## Original source (do not overwrite)
`Character1_NARIS_CHAR022_SkinFixed.glb`, SHA256 `a9389d433d31886c1d4273e6acda0950ca6657fac20338063b9bb643ca95fdd9`.
One Skinned Mesh, one material, three embedded JPEG textures, 18-joint prototype skeleton and one Idle clip, 32,373 original vertices / 49,886 original triangles. Source contains sword geometry within the same mesh as hero. Original binary is unchanged.

## Measured defect
- Original candidate blade geometry has only ~1.13% average influence from `hand_L`; `thigh_L` 31.34%, `calf_L` 24.16%, `foot_L` 20.52%. Existing sword can deform/follow leg skinning instead of being rigidly hand-driven.
- Original candidate guard/mount has `thigh_L` ~42.74% average skin influence and `hand_L` ~16.99%.
- Geometry selection is provisional: components 86–92 for blade and 71/75/78/80/82/84 for guard (529 index-connected components on pinned input); manual visual approval of pommel/hand boundary required.
- In source glTF Y-up units, candidate grip pivot is (-0.2184754, 0.4186020, 0.03518676), proposed bind-pose offset relative to hand_L is (+0.2115246, -0.0613980, +0.03518676). Gap from hand_L origin is ~0.223048 source units, which is not acceptable evidence of an aligned socket.
- Unreal Socket has **not** been created and source coordinates are not Unreal coordinates.

## Minimal, additive review outputs
1. `NARIS_CHAR023_SectionReview.glb` — sections body/guard/blade, original geometry/skin/animation unchanged.
2. `NARIS_CHAR023_HeroWithoutWeapon_REVIEW.glb` — derived skinned body without selected 1,834 weapon faces, still preserves original skin/Idle.
3. `NARIS_CHAR023_RigidWeaponCandidate_REVIEW.glb` — selected 1,834 faces as independent **static** geometry, original UV/normals/material and embedded JPEGs; rest-pose position preserved with node pivot at candidate grip.
4. Exact face balance: body 48,052 + guard 592 + blade 1,242 = original 49,886, no loss. CPU reassembly from actual exported GLBs under matching original projection: 0 changed raster pixels across two views, max 7.4506e-9 source-coordinate offset. This is *not* an actual Unreal screenshot, nor animated validation.
5. Local TDD: 10/10 synthetic small unit tests; 9/9 actual GLB integration tests passed. Three exported GLBs independently loaded by trimesh; embedded original JPEG SHA256 digests match.

## Quality gate and rollback
No original/glTF material is replaced. Do not import both full hero and detached sword simultaneously or weapon will duplicate. Review exports are **not production-ready**: potential mixed hand/cloth fragments, large grip-to-hand mismatch, no confirmed socket transform, animation/attacks/360-degree runtime or physics checks, UE imports/BuildCookRun/network/FPS/memory not run. The 360-degree test is rigid transform algebra only, not a runtime montage test.
Rollback: discard independent review GLBs and retain original; no UE assets, source images, default map or main branch changed. PR remains draft, stacked on CHAR-022 until engine gates.

## 2026-11-18 continuation — original Idle / virtual Socket QA
Reopened the exact source GLB and audited the one real `A_Character1_Idle` animation (chest rotation only, at 0, 0.75 and 1.5 seconds) using the actual glTF inverse bind matrices, four vertex skinning influences and quaternion interpolation. Rig and material source hashes unchanged. A new additive `char023_pose_audit.py` evaluates original weighted sword geometry against rigidly attached hand-relative transforms; `render_char023_pose.py` draws a reproducible CPU before/after and difference heat map.

For 1,119 selected sword vertices and 2,940 unique triangle edges >=1e-5 **source units**, at 0.75 seconds:
- Original weighted mesh: maximum relative individual-edge length change **30.17809%**, mean **0.74642%**, p95 **3.39897%**. The maximum refers to one measured edge, not the whole blade.
- Virtual rigid hand socket: maximum relative individual-edge length change **2.8103e-12 percent** (2.8103e-14 fractional), not a runtime UE result.
- Mean displacement between predicted sword positions **0.00997170 source units**, maximum **0.0160604**. These are pose differences, not confirmed grip misalignment.
- Synthetic wrist rotations 0/90/180/270/360 degrees preserve the local grip constraint and rigid edge length numerically. Source Idle contains no combat/Run/Walk/independent wrist animation.
- Candidate socket offset in **glTF Y-up** is (+0.21152460575, -0.06139798835, +0.03518676013). The ~0.223-source-unit bone-to-grip distance is **not inherently a defect**; socket offsets are expected, and fit/axis/hand contact require visual engine validation. Do NOT copy Y-up values into an Unreal socket without mapping/import checks.

TDD: [RED run 44388350504](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44388350504) reproduced the missing pose-audit module; after minimum implementation, [GREEN run 44388945249](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44388945249) completed 22 synthetic contracts, with two real-original integration suites explicitly skipped on GitHub because original GLB is not in the repo. On the user-supplied GLB locally, **12 synthetic + 4 real-pose tests PASS**; preview regenerated independently and report JSON reproduced exactly.

Complete optional user handoff: `NARIS_CHAR023_RIGID_SOCKET_POSE_QA.zip` (6,866,621 bytes), SHA256 `8f6b6f4f172186458620a2e783f408e7ea6a3c9a8ff7ce095040bbe40d248205`, 14 files, ZIP CRC PASS. Includes original source GLB, existing separated rigid sword and body review GLBs, original Idle CPU before/after preview, test harness, JSON/CSV metrics and reference hashes. No production Unreal assets, sockets, gameplay, animation sequences, maps or packages modified. **NO MERGE** pending manual segmentation/grip and Unreal animation+network+performance quality gates.
Rollback: drop new reports/scripts and independent review assets. Source GLB is preserved byte-for-byte.
