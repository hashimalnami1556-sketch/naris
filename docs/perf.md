# CALL OF NARIS — Performance acceptance and evidence

## Target budgets (project planning; NOT measured production acceptance)

| Area | Target | Tolerable floor / hard ceiling |
| --- | ---: | ---: |
| Desktop gameplay | ≥60 FPS | 45 FPS minimum |
| Minimum-spec gameplay | ≥30 FPS | 25 FPS minimum |
| Frame budget | ≤16.6 ms | 22 ms ceiling |
| First playable load | ≤5 sec | 8 sec ceiling |
| System RAM | ≤6 GB | 8 GB ceiling |
| GPU video memory | ≤4 GB | 6 GB ceiling |
| Packaged distributable size | ≤8 GB | 12 GB ceiling |
| Network tick | 30 Hz | max 60 Hz |
| Intended concurrent clients | up to 8 | tested separately, cap 16 |

These are **goals**, not a claim about measured playable game quality. A small test map or headless `-nullrhi` run cannot establish final production frame rate.

## ANIM-024, 2026-11-21 — actual sampled DEV map baseline (PARTIAL)

- Target test: actual Unreal Engine **5.7.4**, Windows packaged `NARIS_W04.exe`, D3D12 on AsusRog RTX 3050 / i5-14400F, tiny `W04_WolfPresentationV9_Review` test map, **stationary camera**.
- Runtime command: `-benchmark -seconds=30 -ResX=1920 -ResY=1080 -windowed -ExecCmds="csvprofile frames=240"`; Unreal wrote **240 actual CSV frame samples**, 212 columns. Source local machine file `...\PackageReview_WolfAnimNative\Windows\NARIS_W04\Saved\Profiling\CSV\Profile(20261121_055333).csv` SHA256 `E1AB43ECC27B60F6109BE6500D9103DB6F9C31695D82B947843D7A5DEF2C7A2C`. This raw CSV is **not uploaded to this GitHub repo**.
- All 240 frames: mean FrameTime **5.7914ms**, p95 **6.6849ms**, p99 **13.4748ms**, derived FPS-equivalent `1000/mean FrameTime` **172.67**.
- Excluding startup first 60 frames: 180 sampled frames; mean FrameTime **5.5179ms**, p95 **5.9162ms**, p99 **6.9035ms**; derived **181.23 FPS-equivalent**; mean GameThread **1.0361ms**, RenderThread **5.5015ms**, GPU **5.1943ms**, `GPUMem/LocalUsedMB` mean **710.399 MB**. This VRAM-like CSV counter is not the game's total physical usage or evidence of the minimum-spec target.
- The monitor reported **1326×746**, UE metadata `systemresolution.resx=1280` / `resy=720`; the command's requested `-ResX=1920 -ResY=1080` and high-res images are **not independent confirmation** of actual rendering back-buffer resolution.
- `-benchmark` timing, PSO startup outliers (GPUTime max 196.2041ms, RenderThreadTime max 1206.7627ms in all-frame column), default PlayerStart view with 0 camera movement, small review map and no combat/network load mean this is a **numeric tool-validity baseline only**, NOT confirmed whole-game 60fps.
- No matched baseline from the older game binary, no reliable `ΔFPS`, `ΔRAM` or `ΔVRAM` yet. **Production performance gate is OPEN**, not PASS.
- Full report: [ANIM-024 verified UE CSV](changes/ANIM-024/perf_csv_verified_20261121.md). Reusable source parser: `tools/assetforge/anim024_ue_csv_benchmark.py`, tests `tests/anim024/test_anim024_csv_metrics.py`. Test RED→GREEN: [CI 88 failure](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44858513121), [CI 89 success](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44858552592).

## Release-quality performance gate

Measure representative Ashen Forest and combat levels using a fixed Seed, display mode/back-buffer resolution and graphics scalability profile. Record warmup excluded consistently across runs; retain **paired** raw CSV files, logged RHI, screenshot, GPU driver/VRAM and machine spec. Include motion/AI/2-client replication and compare 1st-percentile frame times, GPU/CPU bottlenecks and process working-set. Archive numerical evidence and visual before/after/diff/GIF before merge. A passing compilation, UAT archive or source-only CI is **not** a performance clearance.

The ANIM-024 development PR remains **DRAFT / DO NOT MERGE** until the required original source characters, Montage-notify assets, gameplay animation and network quality gates are met.
