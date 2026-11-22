# LEVEL-001 — Jeddah Realism Pass 02 (review evidence)

Date: 2026-11-21  
Owner-approved scope: Jeddah as independent stage; preserves Ashen Forest/Ash Gate/Bell Marsh/Twilight Citadel.  
Stage: **SOURCE REVIEW ONLY**, not geosurveyed, not running in UE 5.7.

## Why
Pass 01 had photographic-style night references and a procedural 88,540-triangle sector, but no true georeferenced Jeddah footprints, walkable route, Unreal test, or real building photogrammetry.

## What was generated offline
- New separately generated Historic Lane study from procedural PBR source textures (not photos of real buildings).
- Visual GLB: **61,752 triangles**, 31 grouped scene meshes, SHA256 `7f3fc731fadb6ea1f01f9a9dbbd646a1ffac1097f8c4c60ecbca3b9a91936020`.
- Review collision GLB: 156 triangles, 13 mesh groups, SHA256 `5faab5d1217007395ebe49c0d4a8237332a7aa76d048e7f84c6226523e936d9d`.
- Ten authored building shells with geometric 3.6m passage, eight path waypoints, and deterministic seed **20261121**.
- Main-route numerical clearance: 4.5m to model building AABBs. **Does not prove actual UE pawn/collision/NavMesh performance.**
- Before/After/Diff fixed-camera VTK review images, plus 33-frame/3-second real-3D camera walkthrough MP4. None are Unreal screenshots.
- Safe staging-only UE 5.7 Python import prototype: targets `/Game/NARIS/Jeddah/Maps/L_Jeddah_HistoricLane_Review02` and checks for existing level and asset folder to avoid overwrites.

## Evidence / Tests
- 6 Python unittest checks **PASS**; OSM synthetic fixture (1 building+1 walkway) **PASS**; ZIP CRC **PASS**.
- Offline artifact SHA256: `d22bb38262ffb3e7f4c53906c984abe49cc50d88fe05f84d8ba634aa5572b8d3` (`NARIS_JEDDAH_REALISM_PASS2.zip`). Artifact is attached to the ChatGPT conversation, **not stored or uploaded to this GitHub repository**.
- No real OpenStreetMap Jeddah data could be fetched from the execution environment. The authored street layout is **not a real historic-district survey**. The OSM converter remains an opt-in pipeline.
- Unreal import, GLB orientation/pivots, collision runtime, World Partition, Gameplay/Save, server+2 clients, BuildCookRun, `Project.*`, fpschart, 60FPS, VRAM and photo-match: **NOT RUN**.
- Source scripts and binary mesh/media remain in the offline delivered ZIP. This GitHub commit **only records the evidence**; it does not claim those assets are committed or integrated into Unreal.

## Performance and risks
Performance deltas **unknown**. Existing historical Jeddah design and canonical W04 remain unaffected. Procedural materials and symmetric facades are insufficient for real-world photomatch. Passage widths and object pivots must be inspected using a 1.8m pawn inside UE before promotion.

## Review gate / Rollback
Keep PR #113 **draft**, issue #112 **open**. Require city GIS/OSM or survey alignment, licensed façade/scanned materials, and UE 5.7 build/PIE/network/benchmark/visual tests before any merge into production. Rollback: discard review package and this branch's review documentation; existing maps unchanged.

References: [UNESCO Historic Jeddah](https://whc.unesco.org/en/list/1361/) | [OSM copyright](https://www.openstreetmap.org/copyright) | [Cesium placing objects](https://cesium.com/learn/unreal/unreal-placing-objects/) | [UE 5.7 LevelEditorSubsystem](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/LevelEditorSubsystem?application_version=5.7).
