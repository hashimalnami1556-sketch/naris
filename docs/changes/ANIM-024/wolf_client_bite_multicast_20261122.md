# ANIM-024 — remote client Bite Montage playback (22 November 2026)

**Scope and release state:** Unreal Engine **5.7.4**, original source repo `hashimalnami1556-sketch/naris` on **draft, unmerged PR #110**. All actual Unreal experiments on **isolated** `C:\dev\NARIS_ANIM024_20261121\InputReviewProject\NARIS_W04.uproject`; canonical source assets/maps, original project, SaveGames, and Git main were not modified.

## Problem and baseline

The preceding [real server Bite Montage test](wolf_bite_real_montage_notify_20261121.md) proved **server** `AM_Wolf_Bite` playback → existing authored `NarisWolfAttackImpactNotify` → one authoritative `18` HP Boss hit → both clients see `100→82`. But clients received only Wolf Mode=Guard/HP, **not a command to play the Bite Montage**, so no claim of remote animations could be made.

**Baseline:** the previous isolated Win64 Development source backed up, original QA map hashes verified. No new animation binary is required: existing Wolf V9 Bite Montage is real and uses the exact V8-named skeleton object as placed Wolf V9 mesh.

## TDD implementation

Added three source regression cases to `tests/anim024/test_anim024_wolf_boss_combat_probe.py` for server-origin client cosmetic playback and client-authority rejection. [Source Motion Coverage RED](https://github.com/hashimalnami1556-sketch/naris/actions/runs/45009046043) as expected before the code change. Then:
- Declared `UFUNCTION(NetMulticast, Reliable) void MulticastPlayBiteMontageQA();` on `ACelestialWolf`. UFUNCTION declaration exists for code generation; **invocation and actual playback body are under `#if !UE_BUILD_SHIPPING`**, called **only** when opt-in server `-NarisWolfNetProbeMontageOnce` successfully plays server Montage. This is QA-only scaffolding, **NOT a certified production policy for reliable multicast cosmetic events**.
- `MulticastPlayBiteMontageQA_Implementation()`: on the authoritative server immediately returns, because it has already played the Montage. On each relevant client loads **existing** `/Game/NARIS/W04/Characters/WolfPresentationV9/Combat/AM_Wolf_Bite.AM_Wolf_Bite`, plays via local `UAnimInstance::Montage_Play` and logs `ClientMontagePlay authority=0 valid_asset=1 valid_anim_instance=1 duration=...`. No client damage or `CommitAttackImpact` call in this multicast.
- Existing `NarisWolfAttackImpactNotify` can log the real local Notify on clients when `-NarisWolfNetProbe` is enabled. It calls normal `Wolf->CommitAttackImpact()`, where **`!HasAuthority()` rejects immediately** and emits dev-only `ClientImpactRejected`; no client ever applies Boss damage. Server alone performs the hit.

[Source Motion Coverage GREEN](https://github.com/hashimalnami1556-sketch/naris/actions/runs/45009131843): **122 discovered / 120 passed / 2 existing GLB integration skips / 0 failures**. [NARIS Unreal Validate](https://github.com/hashimalnami1556-sketch/naris/actions/runs/45009131866) **PASS**.

**Source safety:** Before patching, compared each of the three current isolated C++ files byte-normalized against separately staged GitHub versions at prior verified HEAD; backed up `Public/CelestialWolf.h`, `Private/CelestialWolf.cpp`, `Private/NarisWolfAttackImpactNotify.cpp` in **`C:\dev\NARIS_ANIM024_20261121\wolf_client_montage_prechange_20261122\`** with recorded SHA256. Source apply audit `wolf_client_montage_source_apply_audit_20261122.json`. Explicit rollback: restore those three local sources and rebuild; earlier retained `PackageReview_WolfRealMontageNotify` is the previous known-good executable.

## Real Unreal Engine quality gates

| Gate | Real result | Evidence on AsusRog |
| --- | --- | --- |
| `Build.bat NARIS_W04Editor Win64 Development -NoUBA -MaxParallelActions=2` | **PASS exit0** (UHT passed) | `wolf_clientmontage_editor_build_20261122.log` SHA256 `b75a06bafa211487258596fa055df6290f2ed367c97f30cc0d9cd8b671d4b9c9` |
| `Build.bat NARIS_W04 Win64 Development -NoUBA -MaxParallelActions=2` | **PASS exit0** | `wolf_clientmontage_game_build_20261122.log` SHA256 `e68695f028ddf25362d8aaa0e27888789b482cb1a1eaf93bb1b55ce3edb5d80c` |
| `RunUAT BuildCookRun -cook -stage -pak -archive` | **PASS exit0**, latest QA archive retained | `wolf_clientmontage_buildcookrun_20261122.log` SHA256 `23a6cb209139c1a346eee0a94ff15e930d626fe24540c8a10ab9475d1f5a3a3e` |
| `Automation RunTests Project.*` using rebuilt editor | `Project.Maps.PIE` **Success; 13 existing warnings, 0 errors, exit0** | `wolf_clientmontage_project_automation_20261122/index.json` SHA256 `b371058fb6f6107f92677f17d3ef70a9d536b222d3b91f110706d1cd8171cd3c` |
| Packaged **one listen server + two clients** | **27/27 strict assertions PASS** | `wolf_client_montage_gate_20261122.json` SHA256 `d80332545297c08b7f72ae29e89d2f9f1114774ecc5f6e4ed74ea2a458a5442d` |

Packaged game kept locally: `C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfClientMontage\Windows` (**not uploaded**).

### Exact network observations

Real local **port 17942**, 1 listen server + 2 cooked `-nullrhi` clients. Two clients both join before single server Bite. **Server**: `ServerMontagePlay authority=1 valid_asset=1 valid_anim_instance=1 duration=0.183`, then authored `MontageNotify authority=1 anim=AM_Wolf_Bite`, then **one** `ServerWolfAttackImpact authority=1 before=100 after=82 damage=18`.

**Each client independently**: `ClientMontagePlay authority=0 valid_asset=1 valid_anim_instance=1 duration=0.183` → authored `MontageNotify authority=0 anim=AM_Wolf_Bite` → `ClientImpactRejected authority=0`. Both initially receive Boss `hp=100 damagefx=0`, then live `hp=82 damagefx=1`, and Wolf `OnRep_Mode mode=1` Guard. No client authority damage and no network/fatal errors in the harness logs. Real independent parser has **27/27 PASS**, including event ordering and unchanged SHA256 of original + previous two test maps. This is **code-execution proof** of client montage playback, **not a visual observation of animation rendering** because the network test used NullRHI.

## Before/after/diff, measurements, limitations

Real static packaged D3D12 `HighResShot 1920×1080` taken from fixed `BugItGo 1100 0 180 -10 0 0` on same disposable map:
- Before from preceding server-only real Montage build: SHA256 `0A1720D2DF521D720A38C927363826805D1FFDAAD104706E65921845E486817E`.
- After from this client-multicast build: SHA256 `6835B7D183657498FCA6F8A532E4E7C69BC11B5EBD231A38538E49BAEF534BC6`.
- **Not visually identical**: bounding rectangle of nonzero pixel difference **(0,427,1920,1080)**. Side-by-side 3840×1080 `wolf_clientmontage_static_before_after_20261122.png` SHA `7332879E153D9841F3FFC221A1FCC71DBFC72E59680CC633B93D719E9B4ACB84`, diff PNG `wolf_clientmontage_static_diff_20261122.png` SHA `814B77FBEEB23E73D1C590B8DD5CD9295FF54746A8E55054D7C9F0D8A45E502B`. This static capture cannot determine whether changes were caused by new C++ source, rendering state, animation phase or uncontrolled environmental variation. **No claim of art improvement or client montage visual match.**

**Real post-change single-run static D3D12 benchmark:** 240 valid uniform CSV frames, first 60 discarded. Mean FrameTime **15.25136ms**, derived FPS-equivalent **65.568**, mean GPUTime **14.40953ms**, local GPU memory used **714.96MB**. Raw CSV SHA256 `dd19848064bb104d7482fd57ddb533097fd774db2a612f0b5a9459354de3a1db`. Prior stage single-run static mean FrameTime **5.73375ms** is **not controlled or statistically matched** to 22 Nov capture; numeric gap **+9.51761ms**, but **no causal performance regression, actual multiplayer player FPS or min-spec certification is established**. Repeat matched seed/time/cache/background load before deciding. The 60fps target is NOT certified by a 65.568 derived single static-frame equivalent. The discrepancy is a quality risk to investigate.

**Safe storage:** The exact new `Saved/StagedBuilds/Windows` (47 generated files / **885,614,981 bytes**) was checked relative-file SHA256 for full equality with retained `PackageReview_WolfClientMontage\Windows`; only verified duplicate temporary staging removed (**0.825GiB freed in that pass**), not previous packages, user content, source or authored assets. `cleanup_wolf_clientmontage_staging_20261122.json` SHA256 `b6262207839c422ad2c1725e6901bc85e2ff0f04cb9ab9188c41950569e482f9`.

## Decision and next gate

**PASS:** Win64 Development compile/cook, PIE, real server/client Bite Montage execution and Notify ordering, server-only Boss HP100→82 replicated to both clients; 27 assertions. **OPEN:** actually inspect client animated poses and frame synchronization with real RHI; authoritative geometry/hitbox collision, quest/gate/save migration and 8-client ownership; **13 old presentation/localization warning causes**, 87-bone hero and remaining missing production Montages; FPS comparison and minimum-spec gameplay load. Reliable multicast is only **developer opt-in QA**; a production-ready general animation event/state policy still needs design and QA.

**PR #110 MUST remain DRAFT / UNMERGED.**

Official references: [Epic networking and RPCs](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine), [Epic Animation Montage](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine), [Epic replicated properties](https://dev.epicgames.com/documentation/en-us/unreal-engine/replicate-actor-properties-in-unreal-engine).
