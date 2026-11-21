# LEVEL-001 — Genuine OSM footprint geometry / Jeddah review V3

Date: 2026-11-21. **Review-only asset generation on the user's authorized AsusRog workstation.** Existing GIS V2 and all Ash maps preserved; do not merge as a shipping level.

## Why
The previously identified real `L_Jeddah_GIS_V2` used actual OSM coords but built rectangular axis-aligned cube proxies for buildings. This review V3 exports **actual OSM building footprint polygons** (not arbitrary boxes), plus roadway ribbon geometry, for a 500m-radius study of Al-Balad.

## Source and production limitations
- Original local OSM-derived cache: `C:\Users\Admin\NARIS\Saved\GIS\Jeddah\jeddah_gis_v2.json` (source OSM contributors, license ODbL 1.0); center WGS84 lat 21.4839, lon 39.1875; GIS world anchor x=25890.85 cm, y=-343779.4 cm.
- Spatial audit: 189 eligible buildings within 500m of center (181 are in original GIS V2's sampled 2200 building actors), 64 eligible road ways included in model.
- Model: `C:\Users\Admin\NARIS\Saved\GIS\Jeddah\LEVEL001_AlBalad_Footprints_Review03\JED_AlBalad_OSM_TrueFootprints_V3.glb`.
- 189 polygon-based extrusions, true outline orientation, simple **proxy** building heights, and actual source road line ribbons; 1,882 wall triangles, 563 roof triangles, 628 roads = **3,073 total**. 260,812-byte GLB. SHA256 `c88acf8243583578e434a8036f6c9dba4c2c0605ccc6a765432e346a2ce28440`.
- GLB uses metres / glTF Y-up; manifest declares GIS world offset and source. OSM building IDs retained. Procedural simple PBR colors only: **NOT photographic facades, no verified Rawasheen, and NOT real surveyed heights**.
- All output files and Python source under `Saved\GIS\Jeddah\LEVEL001_...` or `Saved\GIS\Jeddah\LEVEL001_footprint_glb.py`. They **were not pushed as GitHub assets**. This GitHub PR records provenance and tests only.

## Actual tests
- Red/green TDD for exporter: failing ModuleNotFoundError before implementation, then 3/3 PASS after implementation (concave triangulation, valid GLB 2.0 with preserved OSM ids, no false approval on empty data).
- Existing source GIS tests: 4/4 PASS.
- GLB produced with fixed header/footer length and SHA256; no third-party mesh dependencies.
- A new isolated UE 5.7.4 review map was generated (not replacing `L_Jeddah_GIS_V2`): `/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_Footprints_Review03`, with 3 imported static meshes for walls, roofs, roads, player start, lighting (12 actors total); review import report `LEVEL001_Unreal_Import_Review03_Report.json` says `saved=true`, `asset_exists=true`, `unreal_import_verified=true`.
- **Important:** immediately following editor save, Unreal emitted fatal error `Object is not packaged: ModeManagerInteractiveToolsContext None` on Unreal editor shutdown. Thus `Unreal Editor QA` was NOT clean, even if files exist.
- Direct `-game` launch **successfully loaded** review map and saved a real 1920×1080 screenshot `Saved\Screenshots\NARIS\LEVEL-001_Jeddah_RealFootprints_Review03_after.png`; however the captured view is **mostly occluded by black/white geometry**, matching the unusable before shot. It does not validate the level's geometric view, daylight/night lighting, or spawn clearance.
- Safe isolated camera/WorldSettings correction script is being tested after a saved binary rollback copy of the REVIEW03 map. Do NOT claim it succeeded unless a report and improved runtime screenshot confirm it.

## Gaps / gate
Not measured: FPS, RAM, server+2 clients, Cook+Package, navmesh, collision pawn test, EN/AR, lighting/Lumen, landscape/water, photo scans, building heights and textures. No approved reference imagery or photogrammetry of real Jeddah buildings. The OSM source does not provide building facade fidelity.

Rollback source exists in workstation Saved: `LEVEL001_AlBalad_Footprints_Review03/L_Jeddah_AlBalad_Footprints_Review03_before_camera_fix.umap`. Rollback: restore only isolated review03 .umap if camera patch is faulty; never touch GIS V2. Existing Git working tree remains dirty; do not reset or checkout.

**Do not merge PR #113 or close issue #112 until full artifact QA.** 
