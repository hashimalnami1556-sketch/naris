# ENV-003 precision gate follow-up — 2026-11-04

Executing agent: Codex. Baseline: remote branch head 26bdac69ff8dc986964dc3d7b902d33670d08914. No source geometry, runtime Content, transform or export changed.

Added tools/ci/validate_collision_candidate.py, an explicit preflight command for recorded decomposition measurements. Missing, nonfinite, negative or excessive measurements fail closed. Source files are read and SHA256-checked; duplicates, unsafe paths and upstream failures are rejected. The threshold is controlled by the validator, not an asset's self-reported target. Even an accepted measurement cannot authorize runtime promotion. This checks recorded measurements, not their independent geometric recomputation.

Run from repository root:

```sh
python tools/ci/validate_collision_candidate.py docs/changes/ENV-003/split-decomposition_report.json --source-root /path/to/original/source/files
```

Actual run against both attached original GLBs exited 1 as expected: both candidates rejected. See precision-gate-result.json. Seven new behavioral tests cover invalid/missing measurements, attempted target override, changed source bytes, unsafe/duplicate paths, retained upstream failure and non-promotion of acceptable measurements. Full CI: 424 tests OK; AssetForge: 6 tests OK; repository validator succeeded. These are source/preflight tests, not Unreal tests.

## Next gate: walkable-section authoring (OPEN)

Do not regenerate whole-city hulls simply with a higher hull budget. First establish a documented human-scale factor and bounded route against the original geometry; record floor elevations, door clear widths, stair endpoints and capsule envelope. Author local collision only around this route, preserving archways and courtyard voids. Review front/top/side views, then test both traversal directions and camera collision in Unreal 5.7. No route clearance, manual collider correction, navigation, runtime screenshots, build or performance result is claimed here. UnrealEditor is unavailable in the current executable path.

This CLI is not automatically wired into Unreal import or the absent Change.ps1 pipeline. Invocation and its exit status must be retained with subsequent export evidence. Before/after/diff images are not applicable to this nonvisual validation-code change; prior geometry screenshots remain in the review package. Runtime gate remains blocked. Performance delta unmeasured; no runtime code changed.

Rollback: revert this validation/test/documentation commit; original assets require no restoration. Keep the pre-existing failed geometry finding in force.
