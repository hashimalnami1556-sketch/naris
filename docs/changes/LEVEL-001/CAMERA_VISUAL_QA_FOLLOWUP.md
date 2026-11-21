# LEVEL-001 — Follow-up: actual UE screenshots failed visual acceptance

2026-11-21 — Read-only and review-only execution evidence on authorized AsusRog machine. Does not affect canonical GIS V2 .umap.

## What really worked
- Original `L_Jeddah_GIS_V2` loaded into real UE5.7.4 Editor: MapCheck 0 errors/0 warnings. Actual `-game` load plus 1920×1080 screenshot saved, but photo is obscured.
- True-OSM footprint V3 .glb generated from 189 Al-Balad buildings and 64 road ways; 3,073 triangles; external GLB code passed 3/3 tests; existing GIS 4/4 tests.
- Real Interchange import report `LEVEL001_Unreal_Import_Review03_Report.json` shows three imported static meshes, 12 actors, saved isolated map `/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_Footprints_Review03`.
- Real `-game` launch and 1920×1080 screenshot of review03 passed file-creation/map-load check. Thus a saved `.umap` and live map load are evidenced, **NOT usable gameplay**.
- Binary rollback of REVIEW03 before camera patch saved under `Saved\GIS\Jeddah\LEVEL001_AlBalad_Footprints_Review03\L_Jeddah_AlBalad_Footprints_Review03_before_camera_fix.umap` (34,246 bytes).
- `LEVEL001_Camera_Fix_Report.json`: map saved=true, review world GameModeBase set=true. CameraActor auto-activation **failed** due Unreal Python enum `AutoReceiveInput.PLAYER_0` missing. No replacement of original GIS V2.

## FAILED quality evidence — do not conceal
- Original Jeddah GIS V2 screenshot: `Saved\Screenshots\NARIS\LEVEL-001_Jeddah_GIS_V2_before.png` (1920×1080, 1,375,460 bytes), most of view occluded by near geometry.
- Review03 after screen: `Saved\Screenshots\NARIS\LEVEL-001_Jeddah_RealFootprints_Review03_after.png` (1920×1080, 1,465,999 bytes), similarly occluded.
- GameModeBase/camera patch review screenshot `Saved\Screenshots\NARIS\LEVEL001_Jeddah_Review03_after_camera_fix.png` (1920×1080, 437,198 bytes) is **still nearly black**; not a valid aerial or street-level visual test.
- Editor HighResShot for an aerial shot through interactive python callback timed out (35 simulated seconds) without creating image, so no successful fixed-camera before/after/diff.
- Editor after import emitted fatal `Object is not packaged: ModeManagerInteractiveToolsContext None` after saving; shutdown was NOT clean.
- Not yet tested: packaged Windows BuildCookRun, `Project.*`, NavMesh, collision clearance, Multiplayer (server+2), accessible UI/RTL, photo-match and 60FPS/VRAM.
- Last launched game instance was explicitly stopped after screenshot; no ongoing execution claimed.

## Decision
Keep `GIS V2` unchanged and excluded from Shipping; `REVIEW03` is separate, partially implemented, **not visually approved**. Do not promote until reproducible spectator camera/viewpoint (test correct UE 5.7 enum / world camera activation), road and pawn clearance, realistic licensed facades and PBR/lighting, and performance quality-gate evidence succeed. Restore isolated review03 rollback backup only if necessary; do not discard other dirty working-tree edits.

Issue #112 remains open and PR #113 remains draft. All screenshots and GLB remain on the user's AsusRog; the GitHub branch contains **documentation only**, not binary assets.
