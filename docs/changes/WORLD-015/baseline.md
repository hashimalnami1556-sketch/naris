# WORLD-015 — Actual GLB vertical geometry validation + six editable HUD SVG sources

**Date:** 2026-11-08  
**Engine target:** Unreal Engine 5.7 / Windows.  
**Source branch:** `feature/WORLD-015-vertical-svg`, stacked on `feature/WORLD-014-ground-fix`; not merged.

## Baseline / RED
WORLD-014 verified the horizontal GLB tile footprint but did not validate **imported Z extrema** against the original R16-derived elevations. It could accept an imported 250m×250m terrain whose vertical orientation was inverted or offset. Independent local contract tests reproduced missing `height_min_m` / `height_max_m` metadata and editor-check signature errors. A second test proved a **JSON-only GLB with no vertex BIN data was previously accepted** by a metadata-only validator.

## Fix / GREEN
- **64 real 3D source-derived GLBs / 508,032 triangles** retained, with authentic signed `height_min_m` and `height_max_m` in the tile manifest.
- `tools/assetforge/world015_gltf_gate.py` parses actual glTF2 BIN chunks and vertex/index bytes (not only accessor claims), checks +Y face winding, footprint, topology, and altitude.
- `check_unreal_imported_tile` rejects wrong Z bounds from Unreal `StaticMesh.get_bounding_box()`, including different cm / metre import scaling.
- External `NARIS_WORLD_015_REAL_UE57_SVG.zip` contains corrected full UE authoring Python, verified R16, 5 untouched original GLBs, 3 untouched approved UI PNG references, and six new **editable original SVG** HUD icons with their transparent PNG Texture2D import copies.
- The six SVG source files are committed at `docs/ui/vector_sources/WORLD-015/` (health, energy, mana, attack, defense, map), intentionally not substitutes for the owner-approved images.
- `tools/windows/Invoke-NarisWorld015.ps1` refuses map/asset overwrite and validates the external source package *before* optionally invoking `UnrealEditor-Cmd.exe`. It targets only `/Game/NARIS/W04/Maps/W04_AshenForest_Work015` and does NOT change `GameDefaultMap`.
- `.github/workflows/world015-assets.yml` and source-level Python/6-SVG tests added.

## Real local evidence
- Original `NARIS_WORLD_014_REAL_GEOMETRY_UE57.zip` was inspected in the filesystem; no imaginary sources used.
- Original input and approved UI images SHA256: **unchanged**.
- 43/43 package Python unit tests **PASS** locally, including real GLB parsing; explicit failure-before/fix-after tests.
- Python syntax compilation: PASS.
- Strict package source integrity preflight: `OFFLINE_PASS`.
- New package ZIP CRC: PASS; **111 archived files**, **69 GLBs (64 tiles + 5 originals)**, **6 SVG**, **6 UI PNG icons**, and **3 approved full-screen original PNGs**.
- Package `NARIS_WORLD_015_REAL_UE57_SVG.zip`: **25,285,410 bytes**, SHA256 **`1a8ef6b722f3bf1715af2142c21d661720cb49ac6593474986c9a51cded63eda`**.
- In-GitHub CI results to be collected from the PR; do not infer engine integration from offline results.

## Engine and release blockers (not completed)
- No authorized Unreal Windows host: Remote Desktop Commander rejects link, and alternative remote connectors have no paired machines.
- **NOT RUN**: Unreal editor import, save/open of new `.umap`, PIE, actual native UMG hookup for six icons, A11y/Arabic RTL and new UI screenshots, screenshot before/after/diff, Development build / BuildCookRun, `Project.*` automation, server + 2 clients, FPS/VRAM and Windows EXE installation.
- Real source characters: the sole original rigged prototype contains **18 bones**, not the 92-bone production rig; not promoted as gameplay-ready.
- Original scatter map has **2,990 positions across 9 kinds**, but no verified original static mesh per category, so **0 actor placements** are claimed. Avoid inventing props.
- GLB material shading, Y-up import behavior and world geography still require an in-editor visual review; static scripts alone are not proof of AAA quality.

## Rollback
Use isolated Work015 asset namespace; do not modify existing map or `GameDefaultMap`. Revert this feature PR if the UE import fails. Delete only reviewed, generated Work015 assets after confirming no manually authored dependencies. Preserve all original GLB and owner-approved PNG sources.

## Required next action at authorized UE5.7 host
Run `python Tools/verify_world015_package.py .` in extracted package; execute `tools/windows/Invoke-NarisWorld015.ps1 -PackageRoot <extracted-package-root> -RepoRoot <repo-root> -RunEditor`, verify 64 tiles + original actors + 3 approved reference textures + 6 icon textures; then capture fixed-resolution before/after/diff, PIE, collisions, movement, Arabic RTL, net sync, FPS, Cook and automation. **Draft only; no merge until true engine quality gates pass.**
