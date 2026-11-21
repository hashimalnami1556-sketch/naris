# LEVEL-001 — Actual Unreal camera/lighting before–after QA (2026-11-21)

## Scope and evidence status
**Review only; not shipping.** Jeddah GIS V2 original is unchanged. User asked to see before/after and continue. These captures were produced in **actual Unreal Engine 5.7.4 game sessions**, not rendered concept art.

Local project: `C:\Users\Admin\NARIS\NARIS.uproject`. Isolated review map: `/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_Footprints_Review03`.

## Captures from AsusRog
| Image on local workstation | Verification | Conclusion |
| --- | --- | --- |
| `Saved/Screenshots/NARIS/LEVEL-001_Jeddah_GIS_V2_before.png` | 1920×1080 Unreal `-game` screenshot, saved | Original camera is occluded by geometry; not a usable city view |
| `Saved/Screenshots/NARIS/LEVEL001_Jeddah_Review03_after_camera_fix.png` | 1920×1080 Unreal `-game` screenshot | GameModeBase / earlier camera tweak still produced near-black horizon |
| `Saved/Screenshots/NARIS/LEVEL001_Jeddah_Review03_AerialCamV2_after.png` | 1920×1080 Unreal `-game` screenshot | **Camera successfully moved to aerial**, but normal Lit mode is severely under-illuminated |
| `Saved/Screenshots/NARIS/LEVEL001_Jeddah_GIS_V3_Unlit_Geometry_QA.png` | 1920×1080 Unreal `-game` screenshot with `viewmode unlit` | True OSM geometry and road ribbons clearly visible, proving 3D assets load and view correctly. **Unlit mode is only a structural debug visualization, not a night lighting improvement** |
| `Saved/GIS/Jeddah/LEVEL001_AlBalad_Footprints_Review03/LEVEL001_Aerial_Lit_vs_Unlit_QA_v2.png` | Side-by-side montage at the exact same aerial camera/viewpoint | Left = failed Lit; right = Unlit geometry QA. Do not label right image photoreal or gameplay-approved |

Camera control solved by using the **correct UE5.7 enum**: `unreal.AutoReceiveInput.PLAYER0`, not `PLAYER_0`. Camera V2 persisted and the report `LEVEL001_Camera_V2_Report.json` shows `saved=true`, camera position `[49010.23, -382638.74, 53040.00]` in Unreal centimeters, and material geometry bounds covering about 1 km. SkyAtmosphere was added. Correct visual presence was confirmed via Unlit capture.

### Test matrix
- GLB 2.0 topology exporter tests: 3/3 PASS, GIS source tests: 4/4 PASS.
- Actual Unreal map load: PASS for GIS V2 and review03. At one editor load MapCheck found 0 errors/0 warnings.
- Review03 camera auto-activation from aerial angle: PASS, game runtime images captured.
- Nighttime Lit visibility / physical lighting: **FAIL**.
- True photogrammetry/rawasheen/facade texture match, heritage rights clearance: **NOT IMPLEMENTED**.
- Gameplay navmesh, server + two clients, 60FPS, VRAM/RAM benchmarks, BuildCookRun, Project.*: **NOT RUN**.
- Binary asset GitHub commit: **NOT DONE**; all GLB/.umap/png artifacts remain on workstation.

## Why full lighting test stopped — root cause verified
On retry, UE 5.7.4 `LogShaderCompilers` reported:
```
Could not write the shader compiler transfer filename ... (Free Disk Space: 0)
Error flushing file ... (112: There is not enough space on the disk.)
ShaderCompileWorker expecting input version 32, got 0 instead
```
**This is proven disk-exhaustion / truncated compiler-transfer input**, not grounds for assuming the shader compiler installation is outdated. Current C: free space observed at ~0.19 GiB. Stopped only the Unreal editor game sessions started for this Jeddah review.

Separate actively running workflows were found on the user's computer: an unrelated PowerShell process executing `C:\dev\NARIS_ANIM024_20261121\perf_console_probe.ps1` consumed ~20.8 GiB RAM; another `UnrealEditor-Cmd.exe` process was importing Ash Wanderer assets for a distinct project and consumed ~3 GiB. **These workflows were not interrupted or killed**. Disk-pressure cause is independently confirmed; the exact provenance of all consumed disk bytes is not established. Broad cleanup needs authorization.

## Safe next move / rollback
1. Do **not** run heavy Unreal shader/build jobs with free disk ~0.2 GiB; obtain authorized disk capacity (project policy forbids arbitrary mass deletion).
2. Avoid overlapping shader compilation with other ongoing Unreal workers and high-RAM workflows.
3. Once enough free space is verified, run `Saved/GIS/Jeddah/LEVEL001_evening_lighting_v1.py` in editor, with pre-existing rollback `Saved/GIS/Jeddah/LEVEL001_AlBalad_Footprints_Review03/L_Jeddah_AlBalad_Footprints_Review03_before_evening_light.umap`.
4. Capture genuine **Lit vs Lit**, same camera/seed/resolution/quality. Only then generate diff, after visual QA and performance metrics, test game navigation/network/build. Existing `L_Jeddah_GIS_V2` stays unchanged and excluded from shipping.
5. Keep GitHub issue #112 open, draft PR #113 unmerged; prevent false-ready claims.

Official refs: [UE5.7 AutoReceiveInput](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AutoReceiveInput?application_version=5.7), [UE viewport view modes](https://dev.epicgames.com/documentation/en-us/unreal-engine/viewport-modes-in-unreal-engine), [OSM attribution](https://www.openstreetmap.org/copyright).
