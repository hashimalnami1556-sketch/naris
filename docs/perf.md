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

## ANIM-024, 2026-11-21 — actual replicated Wolf movement and paired net-code DEV benchmark

**Networking quality (not GPU FPS):** UE5.7.4 packaged Development `PackageReview_WolfNetMarch`, one listen server + two packaged clients on loopback `127.0.0.1:17927`, all `-nullrhi -NarisSkipFrontEnd -NarisWolfNetProbe`; server additionally `-NarisWolfNetProbeFollow -NarisWolfNetProbeMarch` *only under `!UE_BUILD_SHIPPING`*. Both clients received replicated Bonded/Follow and nonauthority state, and moved while server Wolf moved. Actual per-run server delta **467.65cm**, clients **37.21/41.18cm** over their own sampled windows; final server↔client positions were within **94.96/8.87cm**, but recorded at differing timestamps and **not** a latency/error or game-quality benchmark. **True combat replication, automatic player-follow target selection and animation remain OPEN.**

**Single-package D3D12 DEV perf A/B with no active network:** same small cloned Wolf visual map and requested `1920×1080` CLI, actual same-camera `-benchmark`, 240 frames each, warmup first 60 excluded:

| Counter | Before source authority fix | After authority fix | Observed Δ |
| --- | ---: | ---: | ---: |
| Mean `FrameTime` | 5.58739ms | 5.56408ms | **−0.02331ms** |
| Derived `1000 / mean(FrameTime)` | 178.974 equivalent | 179.724 equivalent | +0.750 equivalent |
| Mean `GPUTime` | 5.28820ms | 5.26875ms | −0.01945ms |
| Mean `GPUMem/LocalUsedMB` | 711.929MB | 714.932MB | **+3.003MB** |

Real raw before CSV SHA256 `408C64E64C0BFD22FA6FD9DF15EAF4AF82A122503B868535B469A800A70D22D8`; after CSV SHA256 `5D9B745E712ADD4865BF52B4801B0E7DE44FAE598787EE3F057C1CCC5D2604D8`. 1 pass each, full rendered framebuffer and same Seed/animation phase not independently certified. **No claim of +0.75 gameplay FPS** because both samples use static DEV Benchmark with menu pause, not two-client real gameplay rendering. No representative VRAM/RAM/first-load budget clearance.

**Full trace:** [Wolf server-authoritative replication QA](changes/ANIM-024/wolf_authority_replication_verified_20261121.md), local `wolf_net_march_perf_pair_verified.json` SHA256 `262B245F6345530D1E7FBB36EF0548F5F112D7326C61BF41820E4EB4752A8A44`. Release: **ANIM-024 still draft/blocked**. Use actual high-fidelity moving game level, original assets, Windows min spec, fixed Seed/viewport/quality, authoritative inputs and actual two-client D3D12 gameplay for production FPS gate.

## ANIM-024, 2026-11-21 — client-owned Hero RPC evidence and single-pass DEV A/B

**Real network quality:** After earlier server + 2-client Wolf movement QA passed, final Win64 Development isolated `PackageReview_WolfClientCommands` tested **one listen server + two clients on loopback 127.0.0.1:17934**. Client1 (the only instance with developer `-NarisWolfNetProbeInput`) sent Wolf interaction RPC: server **rejected** invalid/non-nearest-or-out-of-range target, proving server validation. Client1 invoked the normal `CycleCompanionMode()` method from a one-shot source probe; server received `ServerCycleMode` with authority=1; **both clients received `OnRep_Mode mode=1` (Guard)** after initial Follow=0. No attack/damage, full gamepad/key action or positive quest bonding tested. Strict local `wolf_client_commands_gate_verified.json` gate PASS, SHA256 `A30D3A0F1CF2F5C9D4A4B22C743A0487FFC34F1B672C8B76E14F4D92198D07AC`. Server-only `-NarisWolfNetProbeNoSave` prevents QA valid-interaction mutation.

**Real D3D12 single-player paused developer map benchmark**, same `BugItGo 1100 0 180 -10 0 0` camera / requested 1920×1080 CLI, 240 samples per run, first 60 frames excluded (180 analyzed):

| Metric | Before input-RPC test source | After input-RPC test source | Observed after − before |
| --- | ---: | ---: | ---: |
| Mean `FrameTime` | 5.56408 ms | 5.57992 ms | **+0.01584 ms** |
| Derived `1000 / mean(FrameTime)` FPS-equivalent | 179.724 | 179.214 | −0.510 equivalent |
| Mean `GPUTime` | 5.26875 ms | 5.28018 ms | +0.01143 ms |
| Mean `GPUMem/LocalUsedMB` | 714.932 MB | 711.951 MB | −2.981 MB |

Raw BEFORE CSV SHA256 `5D9B745E712ADD4865BF52B4801B0E7DE44FAE598787EE3F057C1CCC5D2604D8`; AFTER `22BC8073B117F3886AB72E07B3FBDE8005F06006A197849705AA09DBA894032A`. Local `wolf_client_commands_perf_pair_verified.json` SHA256 `8F1AB9184ACBC01F66110AF7791609D41C47EAA9747DDEBD5B21C06FEEE280F5`. **Uncontrolled single pass; no gameplay/min-spec FPS claim**, and not a GPU-active 2-client benchmark. Actual same-camera before/after 1920×1080 screenshots were **byte-identical**; zero-pixel diff (no art changes), not a moving attack screenshot.

**QA gates:** NARIS_W04Editor / NARIS_W04 Win64 Development builds and UAT BuildCookRun **PASS**, 510 cooked packages; Project.Maps.PIE **Success with 13 existing warnings, 0 errors, exit 0**; GitHub source suite **101 discovered / 99 passed / 2 skipped**. Full [client-owned Wolf RPC test evidence](changes/ANIM-024/wolf_client_owned_rpc_live_20261121.md). ANIM-024 remains **DRAFT / NO MERGE** due missing positive interaction/SaveGame, actual montage combat, 87-bone source/10 Montages and 13 content warnings.

## ANIM-024, 2026-11-21 — near-range client Interact method path and test-map-only performance

**Real network:** one Win64 Development listen server + two cooked clients on localhost:17935 using NEW isolated `W04_Prototype_ANIM024_WolfButtonReview`, copied from WolfLinkReview and moving **only PlayerStart from x=−400 to x=1650cm**, **150cm** from existing Wolf x=1800cm (original map and old clone remain SHA-identical to baseline). Client1 opt-in QA `NarisWolfNetProbeInputButton` called gameplay Hero `Interact()`; **server emitted `ServerInteractAccepted authority=1`** after target nearest/radius validation; client1 `CycleCompanionMode`, server accepted with authority, **both clients replicated Mode=Guard**. Server explicit `-NarisWolfNetProbeNoSave` prevents actual quest/companion persistence. **No hardware input or positive campaign bond, no actual combat**. [Strict 14-check evidence](changes/ANIM-024/wolf_positive_interact_method_review_20261121.md).

Actual packaged D3D12 new test map, requested 1920x1080 and fixed `BugItGo 1100 0 180 -10 0 0`, 240 CSV frames, first 60 discarded, 180 samples:

| New QA map counter | Actual observed |
| --- | ---: |
| Mean `FrameTime` | 5.66648 ms |
| FrameTime p95 | 6.01942 ms |
| FrameTime p99 | 6.75630 ms |
| Derived `1000 / mean(FrameTime)` | 176.476 FPS-equivalent |
| Mean GPUTime | 5.28366 ms |
| Mean `GPUMem/LocalUsedMB` | 714.682 MB |

**Not comparable to earlier WolfLink map:** previously FrameTime 5.57992ms, but PlayerStart and initialization geometry changed in a different local QA map. Numeric cross-map differences (**+0.08656ms**, **−2.738 FPS-equivalent**, **+2.731MB**) have confounders; **authoritative performance Δ=N/A**, not a performance regression or game FPS claim. One-pass single-player benchmark, physical backbuffer and fixed Seed/actual gameplay animation not certified, no 2-client GPU FPS.

Raw after CSV SHA256 **`4159A36B63999268EC15FF0F64E4EC4A24033CEBDFaf2841e6bbb36b9281fcde`**, local before/after comparison report SHA256 **`A2EE92B28323FEC15F585CDC611892FEF64EADAF4D02F4C19F15C12C301D4075`**. 1920×1080 fixed-camera screenshot new map differs from old by wide floor/viewport coverage (expected different spawn/camera setup), so image diff is **not zero**. Actual PIE `Project.Maps.PIE` **success 13 warnings / 0 errors**, Build Editor/Game and UAT CookArchive **pass**. Full report [Wolf positive client interaction](changes/ANIM-024/wolf_positive_interact_method_review_20261121.md). Production release FPS, RAM, VRAM and multiplayer combat performance still BLOCKED.
