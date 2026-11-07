# WORLD-014 — Original environment landmark ground-placement correction

**Target engine:** Unreal Engine 5.7, W04 Ashen Forest.
**Owner art policy:** `docs/DESIGN_PILLARS.md` — preserve original GLB/FBX/USDZ silhouettes and materials.
**Current feature branch:** `feature/WORLD-014-ground-fix` based on WORLD-013, not merged.

## RED: verified defect from WORLD-013
`Tools/build_terrain.py` authored original Environmental 1 and City 1 review landmarks at world Z=0 regardless of terrain elevation; `Tools/ue57_build_world.py` discarded landmark Z and spawned at `unreal.Vector(x*100,y*100,0)`.

| Original source | Before Z (m) | Ground Z from original WORLD-002 R16 (m) | Fix delta |
|---|---:|---:|---:|
| `Environmental 1.glb` — Ashen Forest | 0 | -13.8515625 | -13.8515625 m |
| `City 1.glb` — Twilight Citadel | 0 | -0.015625 | -0.015625 m |

Reproduction: two new local tests failed **before** the patch (wrong anchor height and swallowed Z).

## GREEN: actual fixes in downloadable WORLD-014 handoff
- `Tools/build_terrain.py` calculates each original landmark anchor Z from the same 1009×1009 little-endian R16 as the terrain.
- `Tools/ue57_build_world.py` reads XYZ of each landmark and places actor at `unreal.Vector(x*100,y*100,z*100)`; it validates R16 SHA256 and each landmark elevation **before import**.
- The new review level is isolated as `/Game/NARIS/W04/Maps/W04_AshenForest_Work014` and generated assets are under `/Game/NARIS/W04/Generated/World014`; no production `GameDefaultMap` edits.
- The package launcher uses the documented `UnrealEditor-Cmd.exe -ExecutePythonScript=...` form and refuses a pre-existing authoring report; no previous assets are overwritten.
- Original **5 GLBs and 3 owner-approved PNGs** are byte-identical to WORLD-013. **64 real GLB terrain tiles, 508,032 triangles**, 4 km², and 2,990 original scatter data positions are retained. The nine scatter classes remain unmapped.

## Tests and evidence
- Local test suite for the delivered full package: **27/27 PASS**. This includes 5 pure R16 tests, a source-manifest preflight rejection test, a mocked editor actor-placement rehearsal, and launcher checks.
- `tools/assetforge/world014_ground_alignment.py`, `tools/ci/test_world014_ground_alignment.py`, `tools/ci/verify_world014_package.py` and `tools/windows/Invoke-NarisWorld014.ps1` are committed to GitHub; source binaries and full editor authoring script are supplied only in the conversation download.
- **UNRUN:** Actual Unreal Editor, .umap write and opening, level gameplay, user-visible before/after/diff screenshots, FPS, memory, Development Build, BuildCookRun, `Project.*`, server + two clients, Windows executable installation.
- Device authorization to Remote Desktop Commander currently fails; no access to the Windows Unreal host.

## Current blockers and regression risk
1. R16 anchor Z is now corrected, but the source asset's pivot and mesh bounds can still make the visible art penetrate or hover above the ground; inspect in the engine.
2. glTF metres-to-Unreal centimetres, up-axis, mesh import class, dynamic material response, collision profile and world partition registration require an editor test.
3. The 18-bone prototype is not the 92-bone approved production rig. The original character assets are merely review meshes, not gameplay actors.
4. The PNG references are not interactive UMG widgets.
5. The 2,990 positions do not mean 2,990 meshes have been placed; category bindings are missing.

## Rollback and review discipline
- Separate Work014 namespace; prior prototype map and Work013 remain unchanged.
- Remove only the Work014 level/generated assets after inspecting any manually authored dependencies, or revert the feature branch; leave original assets intact.
- No merge of this draft into `main` or release label until genuine before/after evidence and all engine, performance, localization and network gates pass.

## References
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/LevelEditorSubsystem?application_version=5.7
- https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python
