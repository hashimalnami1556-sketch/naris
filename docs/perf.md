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

## ANIM-024, 2026-11-21 — Wolf mesh link (one-pass DEV A/B, NOT production certification)

After recovering disk space, an isolated `W04_Prototype` was duplicated to `W04_Prototype_ANIM024_WolfLinkReview`, with one existing Wolf V9 `SkeletalMesh` and `ABP_CelestialWolf` added to the clone. Original map/source bytes unchanged; same `BugItGo 1100 0 180 -10 0 0` camera and CLI flags were used for actual packaged D3D12 `-benchmark` / `csvprofile frames=240` runs, each 240 samples. The 180 frames after first 60 were compared:

| Sample | Before no Wolf | After visible Wolf | After − before |
| --- | ---: | ---: | ---: |
| Mean FrameTime | 5.38737ms | 5.58739ms | **+0.20002ms** |
| FrameTime p99 | 5.73096ms | 6.43283ms | +0.70187ms |
| `1000 / mean(FrameTime)` equivalent | 185.619 | 178.974 | **−6.645** (NOT actual interactive FPS delta) |
| Mean GPUTime | 5.08903ms | 5.28820ms | +0.19917ms |
| `GPUMem/LocalUsedMB` mean | 709.397MB | 711.929MB | +2.532MB |

Real before CSV SHA256 `728BB94115094D4D120DFD012A14593DAC8795648EE5318F81E69C15E72514B8`; after CSV SHA256 `408C64E64C0BFD22FA6FD9DF15EAF4AF82A122503B868535B469A800A70D22D8`. Full [ANIM-024 WolfLink review](changes/ANIM-024/wolflink_prototype_review_20261121.md). The first CSV started with 215 columns and added one dynamic late profiling counter after frame 93; a regression test and one-column fail-closed parser fix were committed.

This is an **observational one-pass tiny DEV map comparison**, *not* the release performance gate. Rendering back-buffer resolution was not independently verified, Seed and animation phase were not pinned, shader cache/temperatures were not aligned, and both were `-benchmark` sessions. Gameplay replication was only a login smoke, and BoneBeast/hero/AAA effects remained absent. No credible full-game `ΔFPS`, `ΔVRAM` or 60fps production certification yet.
