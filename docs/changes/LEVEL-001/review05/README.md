# LEVEL-001 — Jeddah Al-Balad Architectural Review V5 (2026-11-22)

**Status: ART REVIEW COMPLETE (Blender), UNREAL RUNTIME / SHIPPING NOT APPROVED.**

## Source of truth and scope

Project on AsusRog: `C:\Users\Admin\NARIS\NARIS.uproject`, Unreal Engine 5.7.
The original `L_Jeddah_GIS_V2.umap` and previously tested `L_Jeddah_AlBalad_Footprints_Review03.umap` remain **unchanged**. Original file SHA-256s checked by automated tests:

- GIS V2: `d77a8aa396827a8ea3a2215196a6c099026b2a245286049488efdd08146e9071`.
- Review03: `00f062c2dcfc172d282c4a9b6855722e0c9ae8969a943de3ff390eb1856ce0e0`.

The geographic basis is **OpenStreetMap contributors, ODbL 1.0**; this selected review sector has **189 real OSM building footprints and 64 road ways** at the documented Jeddah Al-Balad WGS84 center. Building heights are proxy estimates; overlays are artist-designed and not a historical measurement of the individual building.

## Actual implementation

**V4** established geometric stone edge trim and small lattice windows over the OSM source.

**V5** adds:
- **1,158** enclosed, three-dimensional projected rawashin modules, front and side wooden lattice, 0.89m maximum depth;
- **17,370** discrete wooden rails;
- **189** decorative entrance-portal treatments;
- 3 GLB material/mesh groups, **340,308** new detailing triangles, **28,588,796 bytes** V5 GLB.
- SHA-256: `809eeba2f8afe06f74227323c234dca80342fbd4b018253276296a9774842849`.

V4 GLB SHA-256: `27e7a65c1ee3d313fffd5525b3bd00fd8da26ae6b1d746a43613682b154409c0`. The original V3 footprint GLB SHA-256 is `c88acf8243583578e434a8036f6c9dba4c2c0605ccc6a765432e346a2ce28440`. All are stored on the user's workstation under `Saved/GIS/Jeddah/LEVEL001_AlBalad_Footprints_Review0X`; they are **not** asserted to be included as Unreal assets in the GitHub branch.

Portable source/inputs in this branch:
- `tools/level001/LEVEL001_footprint_glb.py`;
- `tools/level001/LEVEL001_facade_v4.py`;
- `tools/level001/LEVEL001_facade_v5.py`;
- `tests/level001/test_facade_v4.py`, `tests/level001/test_facade_v5.py`;
- `docs/changes/LEVEL-001/review04/OSM_Sector189_64_GZIP_BASE64.txt` (selected attributed OSM data);
- `tools/level001/LEVEL001_import_art_review05_UE57.py` (fail-closed isolated Unreal importer).

## Verification performed on actual AsusRog

- V5 functional tests were added **before** implementation: **RED** because its module was absent.
- After implementing V5, **4/4 V5 tests** passed.
- Full offline regression combining V3 / sun-direction record / safe-spawn geometry / V4 / V5 / artifact gates: **26/26 PASSED**, full log `docs/changes/LEVEL-001/review05/offline_tests.log`.
- Python syntax check of the editor importer and source passed. This is **not** an Unreal Python runtime execution.
- **4 new 1440×810 Blender Workbench renders**, exactly matched camera for before(V4)/after(V5), successful. Street sample OSM building ID `1266283904`. A side-by-side JPG/PNG was also generated locally. These are actual rendered GLB meshes, **not Unreal in-game screenshots**.
- Offline integrity test confirmed both original `.umap` files' SHA-256 values above.
- Deterministic V5 GLB test compared independent generated fixture outputs. A further independent reconstruction of **all three real-sector** GLBs was initiated, but as of this report did **not** yield a completed SHA comparison; **do not count that as PASS**.

## Safety constraints and current blocker

AsusRog C: reported **20.72 GiB free**, below the established **30 GiB Unreal work gate**. No heavy Unreal Editor, BuildCookRun, 2-client synchronization or new Lit screenshot was run for V5. The importer requires explicit `NARIS_LEVEL001_REVIEW_IMPORT_APPROVE=1`, correct UE5.7 project, >=30 GiB free C:, unique output names, backup, imported hashes, and duplicated **Review05** level rather than overwriting Review03 or canonical GIS V2.

The 340k extra triangles may require Nanite/LOD/occlusion tuning. The building facades also need manually selected variation and scale calibration to avoid cloned-looking historical architecture. These are not verified historical replicas. No Open Heritage 3D noncommercial scans were incorporated.

## Before merge / final release

- [x] Real OSM footprints preserved, sourced and attributed.
- [x] V5 geometrically extruded, SHA-pinned, test GREEN.
- [x] V4→V5 matched-camera offline preview and 26/26 offline regressions.
- [ ] Reach disk >=30GiB without destructive removal of unrelated content.
- [ ] Actually import both V4 and V5 into new Review05 Unreal level and capture game-engine screenshots (Unlit/Lit).
- [ ] Fix lighting visibility; post-SunFixV3 nighttime Lit screenshot remains missing.
- [ ] Footprint and extended rawashin collision, NavMesh and PlayerStart runtime checks.
- [ ] Third-person playable walkthrough, server + 2 clients; confirm no collision with 0.89m projections.
- [ ] UE Development Build + BuildCookRun + Project.* Automation + stats, FPS/RAM/VRAM budgets.
- [ ] Human visual verification against properly licensed documented Al-Balad references and texture detailing.
- [ ] Verify binary assets via Git LFS, written rollback and versioned changelog; keep PR **draft** until all mandatory gates pass.

## References and obligations

- UNESCO World Heritage Centre: https://whc.unesco.org/en/list/1361/
- Saudi Press Agency on rawasheen construction: https://www.spa.gov.sa/N2385738
- OpenStreetMap attribution / ODbL: https://www.openstreetmap.org/copyright
- Epic Python Editor scripting: https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python

**Rollback:** no source maps changed. To reject this art direction, remove Review05 *generated review-only* artifacts and revert the V5 source-only commit; do not restore or modify GIS V2/Review03. Any future Unreal import must keep its own before/after backups.
