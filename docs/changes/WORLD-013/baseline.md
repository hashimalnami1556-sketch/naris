# CALL OF NARIS — WORLD-013 / UI integrated source, 2026-11-07

**Decision:** move toward one authentic Unreal Engine 5.7 W04 level using the owner's actual models and approved UI screenshots. Do not use screenshot-only impostors, remodel source characters, or change GameDefaultMap to a missing level.

## Before / verified blockers
- On main: `GameDefaultMap=/Game/NARIS/W04/Maps/W04_Prototype`; the requested `W04_AshenForest.umap` is not committed in the expected path.
- WORLD-002 supplies a real 1009x1009 little-endian R16 heightmap for 2km x 2km and `scatter.csv` of 2,990 potential placements, not linked production meshes.
- Nine placement categories have no verified matching original Static Mesh binding. **0/2990 placement actors approved**.
- User-supplied original models: `Character 1.glb`, `Character 3.glb`, `Character1_NARIS_Rigged_Prototype.glb`, `City 1.glb`, `Environmental 1.glb`.
- Three exact original UI PNGs remain owner-approved but are references, not an interactive UMG installation.
- The 18-joint prototype is not the approved 92-joint production rig.

## Actually produced in local artifact
Companion artifact `NARIS_WORLD_013_REAL_GEOMETRY_AND_UE57.zip` (provided in this conversation):
- **64 valid glTF/GLB terrain tiles**, 508,032 actual triangles, built deterministically from the original R16; ~3.968m grid sampling; 4km² extent.
- Unmodified copies of all five original GLBs and all three owner-approved PNGs, integrity SHA256 in local manifest.
- Authoring script `Tools/build_terrain.py`, 64 `Terrain/Chunks/NR_Terrain_R##_C##.glb`, the original R16/PNG and 6-zone/9-route/2990-scatter data.
- `Tools/ue57_build_world.py` targets ONLY `/Game/NARIS/W04/Maps/W04_AshenForest_Work013`, requests `is_partitioned_world=True`, imports the actual original visual meshes and UI textures, adds PlayerStart and lighting, applies terrain-only static collision, and saves the map. **This script has not run inside Unreal.**
- The script never edits DefaultEngine.ini and refuses overwriting prior generated destinations. Camera controls, gameplay Hero and animations must be verified with the existing project GameMode, not assumed.
- Original static character review actors and the original 18-bone rigged prototype are placed only if their import types are verified. Failed rig import becomes an explicit blocker; no substituted hero.
- Two original environment models are placed as REVIEW_SCALE landmarks, collision disabled until manual UCX modeling.
- `Tools/Install-World013.ps1`, `Tests/`, `manifest.json`, `QA_REPORT.json`, `README_AR.md`.

## Code committed on this branch
- Inherits UI-006 changes to the actual UE C++ menu, live inventory panel and live boss bar.
- `tools/ci/verify_world013_package.py`: reproducible source, UI and tile SHA256 gate; protects original bytes.
- `tools/windows/Invoke-NarisWorld013.ps1`: safe offline preflight and opt-in UE5.7 authoring command against the extracted external handoff.
- `docs/DESIGN_PILLARS.md`: preserves the user's final original-art identity decision.
- **Binary source GLB/PNG and 64 terrain GLB binaries are NOT committed here**. Their exact bytes are in the separate downloadable artifact. Git LFS intake remains required before merging into main.

## Actual test evidence
| Test | Result |
|---|---|
| Offline deterministic geometry build | PASS: 64 GLBs / 508032 triangles |
| Mesh topology / adjacent tile seam continuity | PASS |
| WORLD-002 R16 height conversion vs original scatter altitudes | PASS |
| Original source GLB/approved PNG SHA256 comparisons | PASS |
| Local Python regression suite | **16/16 PASS** |
| Python syntax check | PASS |
| ZIP CRC | PASS |
| Unreal Engine 5.7 editor import, World Partition map save | **NOT RUN** |
| 92-joint rig/character animation/actual UMG widgets | **NOT COMPLETED** |
| Before, after, diff screenshots, Windows BuildCookRun | **NOT RUN** |
| Server + 2 clients, FPS, CPU/GPU/RAM, A11y/L10n | **NOT RUN** |

## Quality gate, risk and rollback
**Draft only. No main merge, no shipping claim.** The available Remote Desktop Commander connection returned `link_id must identify an eligible linked account`; there is no accessible local UE5.7 installation.
- Risk: glTF up-axis import and unit scale must be visually verified; actor scale is not automatically production-approved.
- Risk: original environment GLBs are normalized authoring meshes, not 3D equivalents of every image element; nine scatter categories remain unmapped.
- Risk: static terrain complex-as-simple collision is permitted only as a review-map, static non-simulating ground; not for architecture or physics props.
- Rollback: work map has distinct path and no existing maps, saved assets or source files are overwritten; revert isolated feature branch and inspect generated folder before deleting any asset.
- Gates: execute repository `python tools/ci/validate_naris.py`, `python -m unittest discover -s tools/assetforge -v`, local package test; then UE5.7 PIE + Cook + Automation `Project.*`, network, before/after/diff, frame timing and visual approval.

## Next exact blocker to close
Install and execute the downloadable WORLD-013 package in the actual Unreal editor; review generated `.umap`, material orientation, collision and player movement; connect original scene meshes to each scatter kind where evidence exists; import approved PNGs as references and construct actual UMG widgets, then run tests and promote with recorded evidence only.
