# CHAR-022 — original hero GLB skin-binding repair

2026-11-13 | Base: ART-021 reference lock | UE target 5.7

## Measured baseline
Original user asset: Character1_NARIS_Rigged_Prototype.glb
SHA256: 83e4d41f347c959e61ec57355fd682db99ed4652dfabba622ae0784b8cd9b628
18 joints, 32,373 vertices, 49,886 triangles, one material, one original Idle clip (1.5 s, chest rotation only).
Mesh node 18 did not reference the existing skin, so the original animated mesh never deformed. Inverse bind matrices stored with incorrect component order; max bind identity residual 0.9100000262260437.

## Implemented
tools/assetforge/char022_repair_skin.py creates a separate GLB, assigns existing skin 0 to mesh node 18, writes all 18 inverse bind matrices in glTF column-major order using the actual global joint rest transforms, and makes the skinned mesh a scene-root sibling of skeleton root. No new bone, material, texture, mesh, vertex, weight or animation; all binary bytes outside the inverse bind matrix accessor are identical. The original source is never overwritten. Reparenting removes an erroneous 0.05 m inherited rest offset; the repaired bind-pose positions match the original vertex coordinates.

Output: Character1_NARIS_CHAR022_SkinFixed.glb
SHA256: a9389d433d31886c1d4273e6acda0950ca6657fac20338063b9bb643ca95fdd9
Output delivered as external user artifact; binary not committed to GitHub.

## Verified offline evidence
- Bind identity max residual: 0.9100000262260437 -> 0.000000011175870895385742.
- Original 18 joint references/weight sums valid, original geometry/material/image/texture/animation metadata unchanged.
- CPU linear blend skinning, original Idle keyframes 0.00 and 0.75 s: unbound mesh displacement zero; repaired max displacement 0.024678715545867428 m; 21,911 of 32,373 vertices moved by >0.1 mm.
- Ten local Python tests PASS: original fault, skin assignment, matrix identity, identical geometry/weights/animations, binary preservation outside bind accessor, hierarchy, reject invalid weights/already repaired inputs, bind pose, original Idle deformation.
- before_after_pose.png: true GLB triangle/base-color CPU visualization, same camera, not UE screenshot; third panel visualizes displacement, not artistic material.

## Scope boundary and mandatory gates
This repairs an 18-joint prototype. It does not create the agreed production rig, separate cape or sword, Chaos Cloth, collision capsules, weapon sockets, Retargeter, locomotion montages, Foot IK or Unreal assets. Cape penetration is not tested; Blender/Unreal host not available in this turn. No actual editor import, UE compilation, gameplay, networking, FPS/RAM/VRAM, before/after engine captures or BuildCookRun. All such gates remain NOT RUN. No merge or default map modification. Next: import this corrected prototype in an isolated Unreal review folder; verify skeleton and Idle; only then separate cape and test collision before CHAR-023 weapon changes.
Rollback: retain original binary and revert this source-only branch; never overwrite existing authored UE assets.

## 2026-11-14 — Cape review partition, same CHAR-022 change
The source is one welded connected mesh component (1e-6 normalized-coordinate tolerance); cape, clothing, body and weapon are not independently authored objects. A safe candidate-only partition is therefore preferable to destructive automatic cloth segmentation.
- `tools/assetforge/char022_cape_partition.py` adds two index primitives sharing all original vertex attributes, skin and material, based on conservative posterior fabric color/geometry. Output GLB: 30,155 body-review triangles + 19,731 cape-candidate triangles = all original 49,886. Original binary payload preserved verbatim; 18 joints and Idle unchanged. No new bones or weights. 872 shared vertex indices remain across the split.
- Eight local regression tests PASS on the actual pinned SkinFixed source. Tests and algorithm committed; input/output binaries distributed externally, not Git LFS. A three-angle actual-mesh CPU preview highlights the candidate only, not a simulated cloth or true engine before/after.
- Decision: do not assign Chaos Cloth based on this mask alone. Collar/front cloth deliberately excluded; possible upper-arm/dark seam misclassification, no underlying hidden body reconstruction. Manual garment boundary review and a separate simulation mesh are required. No claim of collision-free cape, no Unreal import, PIE, cloth, performance, network or build executed. Remote host still unavailable. Rollback: use unchanged SkinFixed GLB; no overwrite.
