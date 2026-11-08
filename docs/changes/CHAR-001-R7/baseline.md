# CHAR-001-R7 — controlled offline baseline

Date: 2026-11-08 (Asia/Riyadh)
Tracker: #86
Branch: feature/CHAR-001-R7
Main baseline (observed): 0d44d54cacab0443f28f4a11400d544ea4d0941f
Game target: Unreal Engine 5.7, Windows, multiplayer.

## Source bytes (immutable)
- R6 GLB: AshWanderer_R6_MissingActionReference_ONLY.glb
- Source SHA256: `9e687bff68fd9930747485245ae84d68ed2980c31ede4fdad987cfbc46620347`
- R7 GLB: AshWanderer_R7_FlatGround_Reference_ONLY.glb
- Result SHA256: `b35a62d5e422c29194c2d010e1a4733c0a98b54a26ce95a359076bb350821bff`
- GLB and associated test assets are retained in owner-delivered QA package, **not committed to Git**; no Git LFS / Unreal import was executed.

## Repro configuration
- CPU glTF reader and linear skinning: 121 normalized samples per clip.
- Baseline ground reference: Y = 0 metres, flat ground only.
- Metrics are NOT in-engine: max double-length edges = 2.5% provisional, clearance floor = -0.05 m provisional.
- R6 Guard Enter -> Hold / Hold -> Exit: 0.063 m discontinuity.
- R7 equivalent transitions: 0 m in CPU geometric sample.
- All seven R5/R4 animations preserved unchanged in the 12-clip R7 candidate.

## Mandatory Unreal baseline — not captured
- `git HEAD` of local engine project: NOT_AVAILABLE
- Build #: NOT_RUN
- Seed: NOT_SET
- Resolution / quality: NOT_SET (owner gate: 1920x1080 consistent, map L_TestArena)
- Before captures: gameplay, UI, debug, perf: NOT_RUN
- After captures and diff: NOT_RUN
- FPS / frame time / RAM / VRAM / package bytes: NOT_MEASURED
- 1 server + 2 clients: NOT_RUN
- Build.bat Development / RunUAT BuildCookRun / Automation Project.*: NOT_RUN

**Interpretation:** Offline QA data is not a substitute for engine capture, multiplayer test, cook or human review. No promotion to main is permitted.
