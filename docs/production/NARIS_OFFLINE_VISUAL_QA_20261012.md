# NARIS W04 — offline character preview & skinning QA, 2026-10-12

## Verified (outside Unreal Engine)

The owner requested completion, animation tests and pictures of new changes. The model binaries in `NARIS_RIG_EXPANSION_20261012_FULL.zip` were extracted and directly re-tested, not accepted solely from their previously written QA report.

- All **21 original Python unit tests** passed when the complete source bundle was extracted.
- ZIP audit: **35 manifest source entries** match SHA-256.
- **4 additional CPU linear-blend skinning** motion tests passed. Deformed GLB vertices were evaluated with joint global transforms and inverse bind matrices, including dragon WingBeat at 0.48s, Sentinel Light Attack at 0.40s, Beast Claw Swipe at 0.42s and Beast Charge at 0.40s.
- **4 preview-artifact tests** passed, verifying contact sheets and changing frames in both GIFs.
- Overall **29 tests passed / 0 failed** across original, deformation and visualization tests.
- Visual artifacts produced directly from uploaded GLB meshes and textures: character gallery (6 GLB variants); environment gallery (4 GLBs); sampled rest-vs-pose comparison; two 9-frame motion GIFs.
- The images/GIFs and reproducible offline QA JSON/logs are delivered separately in the owner's `NARIS_QA_VISUAL_DELIVERY_20261012.zip` (5.2 MB). Visual binary artifacts are not present in Git history.

### Character geometry truth

The six animated GLBs are **three distinct base meshes with two material treatments each**, not six independently sculpted characters. The four environment GLBs are **two base meshes with two material treatments each**. The so-called *Beast* source visibly resembles a winged humanoid with a sword; its prototype creature rig lacks dedicated wing joints. Retopology, rig retarget/wing weights, visually approved deformations and combat logic are still required.

### Pending, not accomplished

No Unreal PIE, native SkeletalMesh/PhysicsAsset/AnimBlueprint, populated `.umap`, combat/AI/NavMesh hookup, Blender conversion of five USDZ candidates, asset/license validation, cook/package, or 60 FPS benchmark ran. The dragon retains **954,415 triangles** per material variant and must be optimized separately. Preview renders are not in-engine screenshots.

### Merge policy

Keep the staging PR **draft**. Do not promote assets into `data/MASTER_ASSET_REGISTRY.json` as approved, or into production worlds, without actual engine and rights evidence. More local work is blocked by the Desktop Commander account's monthly remote execution quota; the AsusRog device can be online without remote execution rights.
