# ENV-003 actual collision decomposition review — 2026-11-04

Executing agent: Codex. Owner-approved RC1 export files remain unchanged.
Reviewed NARIS_ART_001_COLLISION_RC1_REVIEW.zip: its one-hull-per-city proxy is not suitable for architectural passage collision. No production import was performed.
Executed CoACD 1.0.14 on the two original GLBs, source SHA256 unchanged. Produced 64 convex closed positive-volume hulls per asset and exported two actual FBX files and two Blender authoring scenes with correctly matched UCX names. Blender 4.5.3 reimport matched all render/helper names. Original transforms captured; no physical-scale assumption applied.

## Gate: FAIL — do not promote
City max concavity 0.06830 and Environment 0.11414 exceed requested 0.03 after limiting to 64 hulls. City visual review shows sealed small openings and planar ramps replacing details. The automatic preprocessing/merging cannot certify passage clearance. FBX reimport material appearance was dark: material equivalence is unverified, not passed. Comparison images use original GLB material on the left and colored diagnostic collision on the right.

Unreal import/PIE/traversal/NavMesh/BuildCookRun/performance: NOT_RUN. No game version, playable map, final collision or production gate was approved. Artifact hashes in split-artifacts.json identify review-only files. No binary assets are promoted into Content.

Next: establish human scale and a bounded playable path in each composite source, then author floor/wall/door/stair collision around that route; verify openings and step continuity in Unreal. Avoid treating whole-city decomposition as a modular collision kit. Lighting and gameplay-loop expansion remain gated.

Rollback: discard the review-only package; no original assets or runtime files were changed in this experiment.
