# LEVEL-001 — Baseline (2026-11-21)

## Scope
Documentation-only adoption of the previously designed Jeddah map as a separate CALL OF NARIS stage. No level assets or runtime code are modified.

## Repository
- Base branch: `main`
- Base HEAD before branch: `0d44d54cacab0443f28f4a11400d544ea4d0941f`
- Working branch: `feature/LEVEL-001`
- Tracking issue: https://github.com/hashimalnami1556-sketch/naris/issues/112
- Engine target: Unreal Engine 5.7 (project target; not validated in this change)

## Runtime capture baseline
| Evidence | State | Reason |
|---|---|---|
| Build # | NOT MEASURED | Windows Unreal editor/runner not executed |
| Map | `L_Jeddah_Cesium_Prototype` historical reference, not verified in current repo | No map binary accessible |
| Seed | NOT SET | No runtime |
| Resolution | 1920x1080 target only | No runtime |
| Quality | NOT SET | No runtime |
| FPS / Frame time | NOT MEASURED | No benchmark |
| RAM / VRAM | NOT MEASURED | No benchmark |
| before_gameplay / before_ui / before_debug / before_perf | NOT CAPTURED | No verified running Jeddah map |
| after_* / diff / GIF | NOT CAPTURED | No visual implementation in scope |
| BuildCookRun / Project.* / server+2 clients | NOT RUN | No engine execution in scope |

## Baseline integrity notes
- GitHub code search on default branch for `Jeddah` and `L_Jeddah_Cesium_Prototype` produced no matching indexed source files at review time. Absence from search does not prove absence of unindexed local binary content.
- W04 Ashen Forest has its own shipping gates; documenting Jeddah does not make it shipping-ready.
- Design approval is *not* QA acceptance or production promotion. **No map production completion is claimed.**

## Rollback
Close the draft PR / discard `feature/LEVEL-001` documentation; no existing `.umap`, assets, or game behavior is touched.
