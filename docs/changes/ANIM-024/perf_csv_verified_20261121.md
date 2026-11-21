# ANIM-024 — Verified numeric UE CSVProfiler capture (2026-11-21)

**Status:** numerical baseline for a *developer Wolf review map*, **NOT production performance certification**. This document supersedes the earlier absence of a usable CSV in `real_rhi_perf_probe_20261121.md`, but does not supersede any of its release/screenshot/playability gates.

## Real execution, not a command-line flag

On paired AsusRog, ran the actual **packaged NARIS_W04 Win64 Development executable** from `C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfAnimNative\Windows\NARIS_W04\Binaries\Win64\NARIS_W04.exe`, map `/Game/NARIS/W04/Maps/W04_WolfPresentationV9_Review`, D3D12, with command line:

```text
/Game/NARIS/W04/Maps/W04_WolfPresentationV9_Review -benchmark -seconds=30 -ResX=1920 -ResY=1080 -windowed -NoSound -unattended -NoSplash -ExecCmds="csvprofile frames=240"
```

The previous **`-csvCaptureFrames=180`** direct flag exited 3 with no CSV; the properly quoted `-ExecCmds="csvprofile frames=240"` worked. The engine emitted `Capture Stop requested`, `Capture Ended. Writing CSV`, and `Frames : 240`. File genuinely exists at:

```text
C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfAnimNative\Windows\NARIS_W04\Saved\Profiling\CSV\Profile(20261121_055333).csv
```

**CSV 311,987 bytes**, **212 columns**, **240 numeric frame rows**, plus Unreal's duplicate header and metadata footer. SHA256 **`E1AB43ECC27B60F6109BE6500D9103DB6F9C31695D82B947843D7A5DEF2C7A2C`**.

UE reports D3D12/SM5, engine **5.7.4**, Windows 11, Intel i5-14400F, Nvidia RTX 3050. The Windows monitor reports **1326×746** in the log, while Unreal's metadata reports `systemresolution.resx=1280`, `resy=720`; the requested command line `-ResX=1920 -ResY=1080 -windowed` is present. **Actual frame-buffer render resolution was NOT independently captured**; do not label the following as a certified full-backbuffer 1080p performance result merely because a 1920×1080 HighResShot can be saved.

## Real CSV sample metrics

All duration numbers below are in **milliseconds**. FPS is a **derived equivalent** `1000 / mean(FrameTime)`, not a certified real user-play rate.

| UE CSV metric | All 240 captured frames | 180 frames after excluding first 60 |
| --- | ---: | ---: |
| FrameTime mean | **5.7914 ms** | **5.5179 ms** |
| FrameTime median | 5.4789 ms | 5.4318 ms |
| FrameTime p95 | 6.6849 ms | 5.9162 ms |
| FrameTime p99 | 13.4748 ms | 6.9035 ms |
| FrameTime max | 24.4805 ms | 8.0410 ms |
| FPS equivalent from mean FrameTime | **172.67** | **181.23** |
| 1% low FPS equivalent, 1000 / p99 FrameTime | 74.21 | 144.85 |
| GameThreadTime mean | 1.8531 ms | 1.0361 ms |
| RenderThreadTime mean | 10.7382 ms | 5.5015 ms |
| GPUTime mean | 7.6848 ms | 5.1943 ms |
| GPUTime p99 | 122.2190 ms | 5.7602 ms |
| GPUMem/LocalUsedMB mean | 701.4596 MB | **710.3990 MB** |

**Outlier caution:** startup frames contain PSO creation spikes; e.g. `RenderThreadTime` maximum was **1206.7627ms**, GPUTime max **196.2041ms** even though recorded `FrameTime` max was **24.4805ms**. These UE samples are asynchronous and MUST NOT be treated as perfectly aligned CPU/GPU frame accounting. Unreal's `MemoryFreeMB` is a free-memory column, **not game-process RAM usage**; and `GPUMem/LocalBudgetMB` is a driver budget, not independently verified physical VRAM.

The source CSV has `View/Speed2D=0` across every captured frame: **the camera/player was stationary**. The captured map contains only developer terrain/characters and is **NOT** the full production Ashen Forest with final lights, foliage, physics, VFX, combat, UI and multiplayer clients. Benchmarked `-benchmark` timing is not the same as standard interactive gameplay. **Do not certify FPS≥60, VRAM≤4GB or ΔFPS for the overall game from this result**.

## Reproducibility and fail-closed source tests

New GitHub source-only tool: `tools/assetforge/anim024_ue_csv_benchmark.py`. It rejects missing/nonfinite/zero timings, malformed columns, metadata-only/header-only samples, duplicates, invalid warmup and insufficient frames. It reports `gameplay_fps_certified=false`, `before_after_delta_certified=false` by construction.

```powershell
python tools/assetforge/anim024_ue_csv_benchmark.py "C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfAnimNative\Windows\NARIS_W04\Saved\Profiling\CSV\Profile(20261121_055333).csv" --warmup 60 --min-frames 240 --output "C:\dev\NARIS_ANIM024_20261121\perf_csv_verified_output.json"
```

Original raw CSV is local to the AsusRog device and is **not uploaded to GitHub**, so CI validates the parser with artificial fixtures and does not reproduce the GPU. Read-only local machine analysis file: `C:\dev\NARIS_ANIM024_20261121\perf_csv_verified_240.json` (contains the sample statistics above).

Regression RED [run #88](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44858513121) intentionally failed before adding parser. GREEN [run #89](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44858552592): **86 tests, 84 passed, 2 source GLB integration skipped**. [NARIS Unreal Validate #826](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44858552662) success.

## Additional gates still open

- A genuine **same-Seed/same-camera, same rendering quality, same real viewport resolution** before/after benchmark with paired CSV and matching time/pose. No performance delta asserted here.
- Real multiplayer combat and replicated animation with 1 server + 2 clients; real PSO-warmed walk/run/attack locomotion plus Foot IK.
- Review/approval of 87-bone hero runtime skeleton, 10 exact required production AnimMontages, UI/AR/L10n warnings, final-quality Ashen Forest art and level.
- Validate production GPU and CPU frametimes, process RAM, VRAM/physical budget and first-load time on **minimum target specification**, not a tiny DEV test scene.

**Quality decision: PARTIAL NUMERIC BASELINE ONLY.** Keep ANIM-024 **BLOCKED / DRAFT / DO NOT MERGE**. Rollback is to omit this report/source parser and local CSV harness; no game asset change, destructive cleanup or main merge was made as part of metric retrieval.

Reference: [Epic Unreal CSV Profiler](https://dev.epicgames.com/documentation/en-us/unreal-engine/csv-profiler), [Epic performance profiling](https://dev.epicgames.com/documentation/en-us/unreal-engine/testing-and-optimizing-your-content).
