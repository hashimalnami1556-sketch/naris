# ANIM-024 — GPU performance probe: measurable FPS NOT established (2026-11-21)

**Decision:** graphics-mode packaged execution occurred, but **FPS / frame time / memory Delta are NOT certified**. The local baseline is not tied to a stable Seed or matched before/after render screenshots. This file explicitly prevents a false performance PASS.

## Machine and project
- Isolated packaged Development build from `C:\dev\NARIS_ANIM024_20261121\PackageReview\Windows`.
- Machine: AsusRog, Intel Core i5-14400F, 32GB RAM, **NVIDIA GeForce RTX 3050** (Windows reports 4293918720 bytes of display adapter memory, ~4GiB).
- Target: `/Game/NARIS/W04/Maps/W04_Prototype`, intended 1920×1080 windowed, real RHI (no `-nullrhi`).

## First packaged benchmark trial
- Command-line flags included `-benchmark -fpschart -seconds=15 -ResX=1920 -ResY=1080 -windowed`.
- A real process was started and observed to exit normally with **process exit 0** after timed benchmark termination. UE log `C:\dev\NARIS_ANIM024_20261121\benchmark_1080p.log` recorded `FEngineLoop::Tick.Benchmarking` RequestExit.
- **No FPSChartStats profiling file found** under the initially inspected package Saved location; grep for actual FPS histogram or numerical average found nothing. The probe's raw JSON `benchmark_1080p_report.json` incorrectly sets `fps_measured=true` merely because it found `-fpschart` in the *command-line metadata*. That field is a **FALSE POSITIVE** and MUST NOT be cited as achieved FPS. Preserve raw report; this corrective documentation supersedes the naive boolean.
- A synthetic estimate from frame count/wall time would be misleading because `-benchmark` changes engine time stepping and includes startup overhead. **Do not invent performance numbers**.

## CSV follow-up
- Attempted documented UE `-csvCaptureFrames=180 -seconds=20 -ResX=1920 -ResY=1080 -novsync` using the packaged executable.
- The first invocation generated no game log or CSV file; the controlled Start-Process repetition exited rapidly with code **3**, no `csv_1080p_game.log` and no discovered CSV capture.
- This is a **FAILED PROFILING ATTEMPT**, not an established GPU perf failure or a proved rendering crash: the cause of exit 3 is not diagnosed.
- Local reports: `csv_1080p.ps1`, `csv_1080p_report.json`, `benchmark_1080p.ps1`, `benchmark_1080p_report.json`.
- The controlled harness left **no corresponding packaged NARIS_W04 process** running when checked.

## Remediation gate
1. Investigate why CSV profiling invocation exits 3 without a UE log, and confirm the correct packaged startup command.
2. Use a real render-capable editor/game session to capture **StartFPSChart→StopFPSChart** or `CsvProfile` with actual numeric samples and log/CSV, with fixed target settings and identical Seed/map/camera path for before/after.
3. Record CPU frame, render thread, GPU frame, FPS percentile/average, RAM/VRAM and image diff. Validate 60fps desktop / 45fps minimum (or documented platform spec).
4. Repeat after animation integration and when lighting/materials change. **No perf approval or production release until measured.**

Sources: [Epic command-line arguments](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-command-line-arguments-reference), [Epic CSV profiler](https://dev.epicgames.com/documentation/en-us/unreal-engine/csv-profiler?application_version=4.27), [Epic performance stat commands](https://dev.epicgames.com/documentation/en-us/unreal-engine/stat-commands-in-unreal-engine).

**Status:** ANIM-024 remains DRAFT, **NO MERGE**, `production_ready=false`. Rollback: the perf probes are read-only launch scripts outside original project; do not overwrite the original user build/assets.
