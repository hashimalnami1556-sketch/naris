# ART-001 / COL-001 — RC1 approval intent and collision preflight
Date: 2026-11-04. Owner decision: eight City/Environment assets are **accepted as RC1 candidates** with a target LOD reduction of approximately 15%, preserving original artistic identity under `docs/DESIGN_PILLARS.md`. This is an owner design decision, **not** verification of eight source/export files or a passed Stage Gate 1.

## Observed source evidence
| Available source | GLB meshes | Triangles | Verified LOD1 | Exported UCX | Editor test |
|---|---:|---:|---|---|---|
| `City 1.glb` | 1 | 18,161 | No | No | No |
| `Environmental 1.glb` | 1 | 17,880 | No | No | No |

The two source GLBs have normalized-looking local bounds, but world units are **unknown**. Source meshes were preserved byte-for-byte. Other six claimed RC1 exported files and eight source-to-LOD pairings are not established in currently attached evidence; do not invent them, or set any production registry entry to `approved`.

## Art/collision guidelines
- Create simple UCX convex components named `UCX_<RenderMeshName>_00`, `_01`, etc. Geometry must align with the render mesh in the exported FBX.
- **Do not apply one full convex hull to passable architecture**; it blocks arches/doors. Segment walls around openings, and create a single walkable sloped ramp for stairs where appropriate.
- Require scale/axis verification, simple-collision viewport inspection, walk/run/dodge traversal and clipping checks before accepting.
- Lumen does **not** require baked lighting lightmap UVs. UV generation is conditional on the selected baked-lighting workflow.
- `Combine Meshes` is **not** a blanket performance optimization: it can undermine modular instances/World Partition; assess per kit.
- Nanite and LOD handling must be tested on actual target platforms; do not assume separate LOD1 assets are a Nanite fallback.

## Local deliverable (outside the repo)
`NARIS_ART_001_COLLISION_RC1_REVIEW.zip`: original GLBs, two actual convex-hull review-candidate GLBs (City: 290 triangles, Environment: 400 triangles), offline SHA256/mesh audit, guarded Blender 4.x candidate-FBX exporter and 4 passing local unit tests. These are **review candidates**, not verified UCX collisions or Unreal builds.

## Gating state
- Owner RC1 intent: recorded
- Eight actual LOD assets and 15% measurement: NOT VERIFIED
- UCX Blender export: NOT RUN (Blender unavailable in execution environment)
- Unreal import, Before/After/Diff, BuildCookRun, Project.* automation, server + two clients, FPS/memory: NOT RUN
- Current project device access: unavailable
- Stage Gate 1 **technical pass**: BLOCKED
- Rollback: revert these documentation-only additions; source art unchanged.
- Next: source individual original FBX/GLB meshes and their LOD1s, manually decompose architecture collisions, run Blender + UE5.7/editor tests.

## Change record
Why: avoid fictitious approvals and unblock collision work without replacing original assets.
What: records RC1 owner decision and audited evidence.
How: offline GLB structural/triangle scan and collision candidate production.
Tests: 4 local unit tests PASS, ZIP CRC PASS; Unreal NOT RUN.
Perf: N/A; pending FPS chart.
Risk: convex-hull doors blocked, uncalibrated size/units.
Rollback: revert this doc commit and discard optional collision-candidate outputs.
