# LEVEL-001 — Jeddah real GIS review03 continued: exposure, walkable spawn, sun fix

**Date:** 2026-11-21  
**Status:** IN REVIEW — **not production / not playable certification**. Real authoring, imports and tests were run on the authorized AsusRog workstation against Unreal Engine 5.7.4, with canonical `L_Jeddah_GIS_V2.umap` untouched.

## Geometry & safer PlayerStart candidate
- Generated an OSM-sourced deterministic street spawn selector at `Saved/GIS/Jeddah/LEVEL001_safe_spawn.py`; Python source and tests remain on workstation, not committed to this GitHub branch.
- On actual stored Jeddah OSM cache, preferred pedestrian road **OSM way 45204113**; candidate WGS84 sector (21.4839, 39.1875) maps to Unreal world coordinate **[27632.27, -340805.6, 140] cm**, yaw **132.93°**; location **34.46m** from sector center and **18.57m** geometric clearance to nearest represented OSM building footprint.
- This is *map geometry clearance* only: road alignment and actor collision/NavMesh/Pawn traversability have **NOT** been verified in Unreal. Candidate **not yet applied to PlayerStart**. Output: `Saved/GIS/Jeddah/LEVEL001_AlBalad_Footprints_Review03/LEVEL001_Safe_Street_Spawn_Candidate.json`.

## Lit screenshot and measurement — Exposure V2
- Real in-game 1920×1080 Lit captures from **identical aerial camera**:
  - Before: `Saved/Screenshots/NARIS/LEVEL001_Jeddah_Review03_AerialCamV2_after.png`
  - Evening Lit V1: `Saved/Screenshots/NARIS/LEVEL001_Jeddah_Review03_EveningLitV1_after.png`
  - Exposure diagnostic V2: `Saved/Screenshots/NARIS/LEVEL001_Jeddah_Review03_ExposureDiagnosticV2_after.png`
  - Lit-before vs Lit-after side by side: `Saved/GIS/Jeddah/LEVEL001_AlBalad_Footprints_Review03/LEVEL001_Lit_Before_After_ActualUE.png`
- Fixed-camera diagnostic reference mask: `Saved/Screenshots/NARIS/LEVEL001_Jeddah_GIS_V3_Unlit_Geometry_QA.png` (only for identifying which pixels are mapped buildings/roads; not photoreal or a Lit after image).
- Read-only PowerShell test `Saved/GIS/Jeddah/LEVEL001_lit_visibility_test.ps1`: deterministic 7px sample grid, geometry region from Unlit reference, Lit luminance threshold >=30. Acceptance threshold **50% of sampled mapped geometry visible**, not engine FPS or photo-match.
  - Lit V1 actual result: **4.64%** visible, mean masked luminance 8.02; **FAIL**.
  - Lit exposure bias +5.0 EV: **12.61%** visible, mean masked luminance 21.86; **FAIL**. Increased brightness but did not solve directional light source.
- Diagnostic PostProcessVolume (`LEVEL001_ExposureDiagnosticV2`) saved under isolated review03 with separate rollback backup `L_Jeddah_AlBalad_Footprints_Review03_before_exposure.umap`. This exposure V2 is not an approved scene look.

## Root cause corrected in engine — SUN V3
- A **read-only actual UE Python runtime audit** saved at `LEVEL001_LightMaterial_Inspect.json` showed authored `DirectionalLight` was in fact oriented **pitch +20°, roll -25°, yaw 0°**, with actor light forward vector **Z = +0.342** (pointing *upward*). Original script used positional `unreal.Rotator(-25,20,0)`, incorrectly assuming arguments were pitch/yaw/roll. Actual Python `Rotator` ordering yielded roll/pitch/yaw.
- Same audit showed both DirectionalLight and SkyLight mobility `STATIONARY`, inappropriate for the intended dynamically lit review.
- Wrote a red test `Saved/GIS/Jeddah/LEVEL001_light_direction_tests.py` against real audit: **two failures** (incorrect sun direction, non-MOVABLE lighting). 
- Fixed the *isolated review03 only* in actual Unreal with `unreal.Rotator(pitch=-28.0,yaw=24.0,roll=0.0)`, both lights **MOVABLE**; sun intensity **8500 lux**, warm tint; skylight intensity **1.65**; reduced global diagnostic exposure bias to **+1.5 EV**.
- Actual saved Unreal script report `LEVEL001_SunDirection_FixV3_Report.json` confirms changed forward from `[0.93969,0,+0.34202]` to **`[0.80661,0.35913,-0.46947]`**; saved=true, sun/sky mobility MOVABLE, source GIS V2 preserved. MapCheck showed **0 Errors, 0 Warnings**.
- Four tests of emitted report PASS; full local *non-engine* suite 4 GIS + 3 GLB + 3 spawn + 4 sunfix = **14/14 PASS**.
- Rollback: `Saved/GIS/Jeddah/LEVEL001_AlBalad_Footprints_Review03/L_Jeddah_AlBalad_Footprints_Review03_before_sunfix.umap`.
- **V3 sun runtime screenshot NOT YET CAPTURED / Lit-before-after VISUAL QA NOT PASSED**. The editor shut down, and C: disk free was **28.84 GiB**, below pre-existing mandatory 30 GiB heavy-run guard. Do not claim V3 visual success or performance uplift. Separate worktrees are already dirty, so no git checkout/reset/commit on user's live worktree. Shipping MapsToCook unchanged.

## Release blockers and next executable action
1. Run read-only `Saved/GIS/Jeddah/LEVEL001_resource_preflight.ps1` and require free disk >=30 GiB, free RAM >=8 GiB and no competing UE jobs. Do not delete user or project caches to force passing.
2. Open review03 in UE5.7.4 `-game` with same view, `HighResShot 1920x1080` to new `LEVEL001_Jeddah_Review03_SunFixV3_after.png`. Compare Lit-before vs Lit-after with same fixed camera; rerun geometry-mask visibility test.
3. If V3 passes visual threshold and limited clipping/manual review, apply OSM-derived safe PlayerStart to REVIEW03 only; validate actual ground clearance, NavMesh, pawn motion and collisions.
4. Complete true licensed/original Hijazi facade materials, Lumen/post process refinement, and relevant bilingual/RTL support; Build Development, BuildCookRun, Project.*, server + two clients, fpschart/perf; only then merge draft PR #113 and enable stage in level selection.
5. Heritage photogrammetry `CC BY-NC-ND` remains **not cleared for commercial derivative use** until the requested separate permission is received. No such asset imported.

Official documentation: [Unreal Python PostProcessSettings 5.7](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/PostProcessSettings?application_version=5.7), [PostProcessVolume 5.7](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/PostProcessVolume?application_version=5.7), [OpenStreetMap license](https://www.openstreetmap.org/copyright).
