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
