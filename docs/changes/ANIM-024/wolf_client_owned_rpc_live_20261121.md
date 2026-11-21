# ANIM-024 — Actual client-owned Wolf RPC/validation test, 2 clients, Unreal 5.7.4 (2026-11-21)

**Scope:** Real packaged Win64 Development review `C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfClientCommands\Windows`. Source-only **non-shipping opt-in** QA helper, operating against original Wolf asset in previously cloned `W04_Prototype_ANIM024_WolfLinkReview`. This does **not** approve production network combat, normal button binding, positive gate-based bonding, eight-player companion ownership, or missing animation assets.

## Before / root cause and TDD

Network baseline from [previous moving Wolf test](wolf_authority_replication_verified_20261121.md) had already proven server-authoritative Wolf movement + Mode and Bonded replication to two clients. The **client-owned Hero's `ServerCycleCompanionMode` / `ServerInteractWithWolf` RPCs had compiled and passed source tests but had not been triggered by a real remote client**.

Added four regression assertions to `tests/anim024/test_anim024_wolf_network_authority.py`: opt-in no-shipping client code path, remote Wolf request through client-owned Hero, real `CycleCompanionMode()` method invocation, explicit server accepted/rejected input trace, and server-receipt logging for the mode RPC. **RED:** [ANIM-024 Source Motion Coverage run #125](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44901961413) *failed* by design, while Unreal Validate passed. **GREEN:** [Source Motion Coverage run #126](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44902054461) passed **101 tests discovered / 99 passed / 2 existing GLB skips / 0 failed**, [Unreal Validate](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44902054504) passed.

The minimal additions to `NarisHeroCharacter.h/.cpp`:
- Under `#if !UE_BUILD_SHIPPING` only, client flag `-NarisWolfNetProbeInput` triggers one remote `ServerInteractWithWolf(Wolf)` call ~2s after local possession, then calls the real `CycleCompanionMode()` method ~4s after possession (one-shot phase and clock). Only one specified remote client gets the flag. This **is not** a hardware-button simulation / normal `Interact()` binding test; it validates the production owner-routing RPC path and mode implementation.
- On the server, `-NarisWolfNetProbe` enables developer log events for `ServerInteractRejected`, `ServerInteractAccepted`, and `ServerCycleMode`. **`-NarisWolfNetProbeNoSave`** skips quest/companion/SaveGame mutation if a valid interaction is reached during this explicit QA test. Without these opt-in flags, the production behavior is unchanged.
- No source model, mesh, `AnimMontage`, UI icon, original level asset or SaveGame was rewritten. The two isolated current Hero files were checked against the preceding saved reviewed staging copies before applying, and original C++ bytes were copied to `netpatch_hero_pre_input_20261121` with SHA256 confirmation. Local application audit SHA256 **`887488D02B8802B9C2C2CED678311E7AF82B0C39BB197CFBBC5D07D217AAC74F`**.

## Real build / cook / PIE

| Actual test | Result | Evidence SHA256 (LOCAL only) |
| --- | --- | --- |
| UE5.7.4 `Build.bat NARIS_W04Editor Win64 Development` | **PASS, exit 0** | `wolf_input_editor_build.log` **`814B0497A0E31D3D4782AA6CD773EE7B2EE1C21BFD6449479D38B941C2EAAE65`** |
| UE5.7.4 `Build.bat NARIS_W04 Win64 Development` | **PASS, exit 0** | `wolf_input_game_build.log` **`1960C494286785B13EF2F204EBE6976380F227EBCBD2A2740678E2978B6CF501`** |
| Real `RunUAT BuildCookRun -skipbuild -cook -stage -pak -archive` | **PASS, exit 0, 510 cooked packages** | `wolf_input_buildcookrun.log` **`1F6CC601C35C86D51F3ED29D1DB5B32FA2F613AAE4F3C9965EFA6330ED7F6553`** |
| `Automation RunTests Project.*` inside UnrealEditor-Cmd | **Project.Maps.PIE success, 13 warnings, 0 errors, exit 0** | `wolf_client_commands_automation/index.json` **`4D64BC03574A7426D8DDE4FF00FC3083A4167BE393F2A91C66029458768A4676`** |

**13 warnings remain**: prior missing UI/presentation references, localization and AR material. The release gate remains BLOCKED.

## Actual 1 listen server + 2 clients test

Used fully cooked Developer package on loopback **127.0.0.1:17934**, real Unreal net driver and Character/Pawn instances. All three `-nullrhi -NarisSkipFrontEnd -NarisWolfNetProbe`; server additionally `-NarisWolfNetProbeFollow -NarisWolfNetProbeNoSave`; **client1 only** `-NarisWolfNetProbeInput`. No client ever got the server `NoSave` or `Follow` flags. `-NarisSkipFrontEnd` avoids the existing front-end pausing gameplay; no UI production code modified. All harness-spawned processes were stopped on exit.

Chronological measured log events:
1. Server reports **2 Join succeeded**; both clients report Welcomed and `OnRep_Bonded bonded=1`, `OnRep_Mode mode=0` (Follow).
2. Client1 emits `NARIS_WOLF_NET_PROBE event=ClientInteractRequest actor=CelestialWolf_0 authority=0`; **server actually executes the owning-Hero RPC and emits** `event=ServerInteractRejected authority=1 reason=not_nearest_or_out_of_range`. The server-side nearest-interactable/radius check correctly refuses this proposed target. The diagnostic alone **does not distinguish** out-of-range from another closer actor. No positive bond nor gate permission is inferred.
3. Client1 emits `event=ClientCycleMode authority=0`; the **server** emits `event=ServerCycleMode authority=1`.
4. **Both clients** subsequently receive `event=OnRep_Mode mode=1` (Guard) and hold `bonded=1`, `authority=0` on their simulated Wolf. Server reports `authority=1`, `mode=1`.
5. **0** network/UE fatal error matches in the 3 checked logs. The local package and isolated project had **no** `Saved/SaveGames` directory before or after this test; we did **not** capture OS-wide save state for every possible Windows user profile path, so do not claim globally zero file writes. The explicit QA `NoSave` flag prevents the valid-interact game save path if reached during this test.

Strict independent log gate `wolf_client_commands_gate_verified.json` SHA256 **`A30D3A0F1CF2F5C9D4A4B22C743A0487FFC34F1B672C8B76E14F4D92198D07AC`** reports **`gate_pass=true`** for these narrow assertions. Raw `wolf_client_commands_report.json` SHA256 **`92DF078BEA08032F5B5E3FA4DB783C6E2ED737737C149696275AED176EFC3A5E`**. Raw logs SHA256: server **`64F2E337C4B5D5FA145A7C4B40F16925320A1E0965CE00E71ED86B719D770F92`**, client1 **`F70A9FDC7800C3C9867EA0B634E986BA62DD3405FB27CB091DA2740B3C9EA7E7`**, client2 **`D6124E4903847649AB016EF41F86A4D9CD60E9641D347E45C6C5532FCCE206F3`**.

**Important:** `wolf_client_commands_report.json` reuses the previous harness and reports `movement_replication_verified=false` because the Wolf has already completed the normal Follow approach and entered Guard. This test is specifically **RPC and state**, not a regression of previously verified post-join continuous movement. Earlier `wolf_net_march_clients_report.json` documents actual server + 2-client movement under a separate opt-in march test.

## Same-camera before / after / diff and metrics

- Real packaged D3D12 before (previous WolfNetMarch build) vs after (current WolfClientCommands build) `HighResShot 1920x1080`, `BugItGo 1100 0 180 -10 0 0`, **identical image bytes** and SHA256 **`5031EACDB6DF258808C99CD0EB00F33AE2D187BE457ED1A00698FFCBAB3CCEA2`**. Side-by-side `wolf_client_commands_before_after.png` SHA256 `2CCBA221CF9663CC65989093F9F345B3105AD80D946566343203975F075C5263`; pixel diff `wolf_client_commands_visual_diff.png` SHA256 `0F52608DD021E7069EF19F9D8F46F6D651AAF5CBAC5154465092DE3574CF8514` (black, **zero difference**). This ensures no fixed-frame visual regression, **not** visual confirmation of attack/interaction animations or network clients.
- Real matched developer map D3D12 `-benchmark` and `csvprofile frames=240`, 60 discarded warmup frames, 180 analyzed. User-quality metrics **NOT certified** (single-pass paused scene, 1080p CLI requested but actual backbuffer not independently proven, Seed and temporal pose not fixed):
  
| Counter | Before client owned-RPC QA code | After | Observed Δ |
| --- | ---: | ---: | ---: |
| Mean FrameTime | 5.56408ms | 5.57992ms | **+0.01584ms** |
| Derived `1000 / mean(FrameTime)` equivalent | 179.724 | 179.214 | −0.510 equivalent |
| Mean GPUTime | 5.26875ms | 5.28018ms | +0.01143ms |
| Mean `GPUMem/LocalUsedMB` | 714.932MB | 711.951MB | −2.981MB |

Raw BEFORE CSV SHA256 **`5D9B745E712ADD4865BF52B4801B0E7DE44FAE598787EE3F057C1CCC5D2604D8`**, AFTER **`22BC8073B117F3886AB72E07B3FBDE8005F06006A197849705AA09DBA894032A`**; local `wolf_client_commands_perf_pair_verified.json` SHA256 **`8F1AB9184ACBC01F66110AF7791609D41C47EAA9747DDEBD5B21C06FEEE280F5`**. Do **not** promote the observed small difference to a meaningful FPS/memory optimization.

## Cleanup, source safety and rollback

- Current `W04_Prototype.umap` SHA256 **`2D6D4A2EA4118B41AD0D29EAE4526A78252395F6BAEDF1EBE0D2F11C07D52A81`** and cloned `W04_Prototype_ANIM024_WolfLinkReview.umap` SHA256 **`3EE92BE6C800855BD5542E9B095066772CB7408FD779BE443E9BD32C7965B6C6`**, identical to earlier audited baseline. Original master dirty/untracked work and art not touched, `main` not modified.
- Hash-verified **47 matching files, 885,561,033 bytes** in current `Saved/StagedBuilds/Windows` equal by relative path, size and SHA256 to newest retained `PackageReview_WolfClientCommands/Windows`; removed only identical duplicate stage, reporting **0.825 GiB freed in that pass**. New archive and prior packages preserved. Local audit `cleanup_wolf_client_commands_staging_20261121.json` SHA256 **`C8A6DEE1131D260A74903CD294F74ED8B5FAC6E395BF48D9F8E794820B89D5C6`**. Drive `C:` free **36.524 GiB** after all recooking, not a net source package size metric.
- **Rollback:** remove new client QA commits on draft branch and restore two Hero files from `netpatch_hero_pre_input_20261121`, rebuild Editor/Game, or launch earlier `PackageReview_WolfNetMarch`. Do not delete user's master assets, earlier good archives or crash evidence.

**Decision:** PLAYER-OWNED MODE RPC AND SERVER REJECTION TEST **PASS**; REAL KEYBOARD CONTROLLER `Interact()` / POSITIVE QUEST BONDING / CLIENT GAMEPLAY SAVE / BOSS ATTACK DAMAGE REPLICATION **UNVERIFIED**, and the **production approval remains BLOCKED. PR #110 DRAFT / NO MERGE**.

References: [Epic Remote Procedure Calls](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine), [Epic Actor Ownership](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-owner-and-owning-connection-in-unreal-engine), [Epic Replicate Actor Properties](https://dev.epicgames.com/documentation/en-us/unreal-engine/replicate-actor-properties-in-unreal-engine).
