# CALL OF NARIS — Design Pillars

**Decision: LOCKED / FINAL.** Preserve the artistic identity of every original character and asset (GLB/FBX/USDZ); apply a non-destructive environmental unification layer in Unreal Engine 5. This decision precedes technical changes and overrides earlier photo-realistic rebuild or preview-only directions.

## Why we reject photorealistic rebuilding
1. Rebuilding replaces the user's original assets and contradicts the core project goal.
2. Photogrammetry, high-resolution materials and wholesale relighting delay a playable vertical slice.
3. It does not close G0 skeleton compatibility sooner and can invalidate existing rigging.
4. Photorealism exposes inconsistencies rather than making them intentionally stylized.

## Positive rationale
Retain the unique original silhouettes, meshes, materials and visual languages. Cohesion arises from the Ashen world's ash, fog, light, material response and color grading, while retaining source files and asset provenance.

## UE5 environmental unification layer

| Layer | Implementation | Constraint |
|---|---|---|
| Materials | Shared master-material pattern and per-asset instances, coordinated roughness/specular; cloth/hair wind and skin subsurface only where appropriate | Preserve original PBR maps, surface semantics and distinctive visual identity |
| Lighting | Lumen, Sky Atmosphere, Exponential Height Fog and Volumetric Clouds when performance allows | No destructive geometry edits |
| Post-processing | One consistent Post Process treatment / LUT, cool shadows and warm lights | Protect original color identity and readability |
| Narrative ash | Subtle non-destructive ash/dust decal or material layer | No baked replacement textures |
| LOD / performance | AssetForge inspects models, builds LODs and standardizes material response | Do not remodel assets for photorealism |

## Pipeline effects and acceptance criteria
- **G0:** first inspect actual source and target Skeleton hierarchy, bind pose and skin weights; build source and target IK Rigs, set suitable pelvis/hips Retarget Root, test walk/run, foot sliding and deformation. Do not mark the 92-joint specification as an executed production rig.
- **AssetForge:** material/LOD normalization, provenance and validation, not artistic replacement.
- **World Partition:** retain the connected open-world architecture.
- **QA:** fixed-seed, fixed-quality before/after/diff screenshots from actual UE5, including visual cohesion checks; Build/Cook, automation tests, server + two clients, FPS/memory benchmarks and rollback.
- Rendered concept images are **not** verified level screenshots. Keep originals in Git LFS.

## Change control
Any change to this locked decision requires an explicit revised decision record and approval. Prioritize a playable Unreal level over presentation imagery.

## References
- https://dev.epicgames.com/documentation/en-us/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
