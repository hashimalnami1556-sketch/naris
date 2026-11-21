# ANIM-024 — Server-authoritative Celestial Wolf, real two-client replicated movement (2026-11-21)

**Status:** VERIFIED *partial* network gate for isolated Wolf visual review. **Not** production approval: real client bonding/mode input RPC, authored attack Montage/Notify, authoritative combat damage, full gameplay sync, original map integration, original 87-bone hero, 10 exact animation assets, performance at target spec and final art remain OPEN.

## 1. Baseline, root cause and review scope

Before any code change, read-only UE5.7.4 Editor Python confirmed that **all three** actual placed `ACelestialWolf` Actors in `W04_Prototype`, `W04_Prototype_ANIM024_WolfLinkReview` and `W04_WolfPresentationV9_Review` had `replicates=True`, `replicate_movement=True`, `remote_role=ROLE_SIMULATED_PROXY`. **Do not claim missing replication flags caused this bug**; these are inherited defaults of `ACharacter`.

The original networking defects were in user C++ rather than Actor settings:
- `ACelestialWolf::BeginPlay` read local RuntimeSubsystem save state **on clients**, and `Mode` / `bBonded` were **not explicitly replicated**.
- `Tick`, `RequestAttack`, `CommitAttackImpact`, `BondWithPlayer` and mode/target changes had no `HasAuthority()` barriers, so game decisions/damage could run outside authoritative ownership paths.
- `ANarisHeroCharacter::Interact` and `CycleCompanionMode` called the Wolf on the local instance. A level-placed Wolf is server-owned, so client→server commands must be routed via the **client-owned Hero's Server RPC**, and target/proximity must be checked on the server.
- The first headless network probe used only `-nullrhi` with the ordinary front-end menu, which **paused gameplay** and made the network movement test invalid. **No code change was necessary to bypass this**: project `ANarisPlayerController::BeginPlay` already supports `-NarisSkipFrontEnd`.

**Protected world:** isolated `C:\dev\NARIS_ANIM024_20261121\InputReviewProject`; real binary map `W04_Prototype_ANIM024_WolfLinkReview.umap` SHA256 **`3EE92BE6C800855BD5542E9B095066772CB7408FD779BE443E9BD32C7965B6C6`**, original local `W04_Prototype.umap` SHA256 both before/after **`2D6D4A2EA4118B41AD0D29EAE4526A78252395F6BAEDF1EBE0D2F11C07D52A81`**. No source asset, model, material, `.umap`, `.uasset`, master user checkout or GameInstance save file was overwritten by these QA script changes.

## 2. Minimal source changes, TDD and security boundaries

Modified four *source-controlled* files in draft branch `feature/ANIM-024-source-coverage-gate`:

1. `unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h`: mark `Mode` / `bBonded` as `ReplicatedUsing`, declare `GetLifetimeReplicatedProps`, `OnRep_Mode`, `OnRep_Bonded`, and a transient per-Wolf QA log clock.
2. `.../Private/CelestialWolf.cpp`: `DOREPLIFETIME` both properties; clients receive `OnModeChanged` / `OnBonded` callbacks via `OnRep`; `HasAuthority` protects movement/combat/quest/save state. Clients cannot apply Wolf boss damage in `CommitAttackImpact`. Includes opt-in `-NarisWolfNetProbe`, `-NarisWolfNetProbeFollow` and `-NarisWolfNetProbeMarch` **only** inside `#if !UE_BUILD_SHIPPING`. March uses **real** `MoveTowards` / `AddMovementInput` and a deterministic moving in-memory destination. It does not change the normal player-follow algorithm, asset contents or save.
3. `.../Public/NarisHeroCharacter.h` + `.../Private/NarisHeroCharacter.cpp`: new `UFUNCTION(Server, Reliable)` RPCs `ServerInteractWithWolf` and `ServerCycleCompanionMode` owned by the player Hero. Server checks the passed Wolf exists and **equals the nearest server-side interactable**, which enforces the configured interaction radius. **Existing non-Wolf interactions unchanged.**

TDD: added `tests/anim024/test_anim024_wolf_network_authority.py`, initially RED [CI #113](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44879038851) before authority/RPC implementation, then GREEN [CI #117](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44879165873). A separate moving-probe regression was intentionally RED [CI #119](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44879996703), then [CI **#120 GREEN**](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44880048756): **97 discovered, 95 passed, 2 existing GLB integration skips, 0 failed**. [NARIS Unreal Validate #847](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44880048761) **PASS**. GitHub CI validates source contracts; it **does not have an Unreal runtime or GPU**.

**Local source backup** `C:\dev\NARIS_ANIM024_20261121\netpatch_source_backups_20261121` for all 4 original C++ files, plus `netpatch_wolf_cpp_pre_march.cpp` for intermediate state. Actual patch audit `netpatch_apply_audit_20261121.json` SHA256 **`E23C79B9C27DF243486FAB4582A0076DB0A5B52118B8ED3A72EEE66F3FD92288`**.

## 3. Real UE5.7.4 build/cook/automation QA

All on AsusRog isolated `NARIS_W04.uproject`, UE5.7.4, Windows Development:

| Gate | Actual result | Local evidence SHA256 |
| --- | --- | --- |
| `Build.bat NARIS_W04Editor Win64 Development` after authority/RPC | **PASS, exit 0** | `netpatch_editor_build.log` `D2C3537A9D77682A97A91D0A1AC73C629E462529474901E29F1E0320E3B5A120` |
| `Build.bat NARIS_W04 Win64 Development` | **PASS, exit 0** | `netpatch_game_build.log` `43BCF0B964C9A12D21A58FCCC521C3A5C6BAB80ACCC788A56FFE2FF5BEE7E080` |
| Final source after march probe, Editor + Game builds | **BOTH PASS, exit 0** | `wolf_march_editor_build.log` `81B94666EDF2576BE709DD99C3BB41750236F81F23C68D01222A6EBBFE331CBA` and `wolf_march_game_build.log` `FA8281DD0B6F628B60797A75A752B3C3F6EA4EDC01AD7C4F3731398E53620E7D` |
| Final `RunUAT BuildCookRun -cook -stage -pak -archive -skipbuild` | **PASS, 510 cooked packages, exit 0** | `wolf_march_buildcookrun.log` `608E38801CBD0CE903B99D12ECD121908830984ACFAA20B05A48F87BB76A5931` |
| UE `Automation RunTests Project.*` | **Project.Maps.PIE Success, exit 0, 0 errors, 13 warnings** | `wolf_net_march_project_automation\index.json` `AA916D0BB22BAD0F44D288BCA9970BFEA07B6F26C8337E1C8784A6816217DD58` |

**Final package retained:** `C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfNetMarch\Windows`; prior good archives `PackageReview_WolfLinkReview`, `PackageReview_WolfAnimNative` remain for rollback. Actual PIE warnings (icons/AR/localization) are **not fixed**; the launch smoke and clean compiler **do not clear the release gate**.

## 4. Actual network evidence — RED, diagnosis and GREEN

**Test 1, paused:** one listen server + two clients connected, but front-end pause blocked meaningful time-dependent movement; one client received the replicated Mode/Bonded and the other did not log it. **Status: INCONCLUSIVE for gameplay.**

**Test 2, unpaused:** added existing CLI `-NarisSkipFrontEnd` on server and clients, and server QA `-NarisWolfNetProbeFollow`:
- Server initially moved Wolf from **x=1800.00cm → 1354.10cm** before clients joined, then naturally stopped within follow acceptance radius. Two clients received **`OnRep_Mode mode=0`** (Follow), **`OnRep_Bonded bonded=1`**, and logged **`authority=0`** with replicated position **x=1354.10cm**.
- Initial position + state replication proved. **Post-join movement not proven**, because it was already stopped.

**Test 3, GREEN:** fully cooked final Developer package, one `?listen` server, two real packaged `-nullrhi` loopback clients on port **17927**, all run with `-NarisSkipFrontEnd -NarisWolfNetProbe`, **server only** `-NarisWolfNetProbeFollow -NarisWolfNetProbeMarch`. While both clients were connected, the Wolf followed an oscillating, deterministic QA destination **through real CharacterMovement**, and its server-owned position updates replicated:

| Measured telemetry | Server | Client 1 | Client 2 |
| --- | ---: | ---: | ---: |
| Net probe `Tick` log samples | **18** | **14** | **13** |
| `authority` | **1** | **0** | **0** |
| `bonded=1, mode=Follow` | YES | YES, `OnRep` received | YES, `OnRep` received |
| First → last X (cm) | 1800.00 → 2267.65 | 2325.40 → 2362.61 | 2317.70 → 2276.52 |
| Position movement over its own sampled window | **467.65cm** | **37.21cm** | **41.18cm** |
| Final sampled position distance from last server X | — | **94.96cm** | **8.87cm** |

Both clients were welcomed and the server recorded two successful joins; harness `success_handshake=true`, `replicated_bond_and_mode=true`, **`movement_replication_verified=true`**, `combat_replication_verified=false`. Different log sample times mean these X differences **are not instantaneous latency/error measures**, nor proof of frame-perfect animation.

Unmodified raw local `wolf_net_march_clients_report.json` SHA256 **`2984D6698186755D6487F23AC335FF90DEF3986852912EA366F93341F2214057`**. Server/client logs SHA256:
- server `1C411CDE71C19C1BD8C9AF774B1C36463BCE9B307FB2727354BA35C9A235BA7B`;
- client1 `406F812250886AFCD651498B7211515648451E03B21C895FBA65818C49CDEC7C`;
- client2 `4F72045E0DC41278EDCE008C2254884B515CA3330442BC6808F05079339E7CDF`.

All harness-spawned packaged game processes were stopped after inspection. **No combat was triggered**. `bBonded` was activated only via the QA server flag—not through actual player interaction, quest-gate unlock or SaveGame workflow. The **player-owned RPC code compiles and passes source contract tests**, but end-to-end client button interaction/authority/damage remains unverified.

## 5. Before/after/diff and numeric performance (scope-specific)

**Visual:** actual packaged D3D12 same-camera `BugItGo 1100 0 180 -10 0 0` at `HighResShot 1920x1080` before and after the networking C++ change. Old `wolf_prototype_after_assetlink.png` and new `wolf_net_march_after_1080.png` are **byte-identical**, each SHA256 **`5031EACDB6DF258808C99CD0EB00F33AE2D187BE457ED1A00698FFCBAB3CCEA2`**. New side-by-side `wolf_net_march_before_after.png` SHA256 `2CCBA221CF9663CC65989093F9F345B3105AD80D946566343203975F075C5263`, new diff `wolf_net_march_visual_diff.png` SHA256 `0F52608DD021E7069EF19F9D8F46F6D651AAF5CBAC5154465092DE3574CF8514` (null pixel difference). This *only* confirms render unchanged in that paused frame; neither a game art improvement nor a locomotion GIF.

**Real D3D12 CSV:** fixed requested `-ResX=1920 -ResY=1080 -windowed` and same camera/benchmark command, one genuine **240-frame** CSV each, excluding 60 startup frames. Physical back-buffer size/quality preset, Seed/animation phase, CPU/GPU temperatures and background work **not controlled**, so this is *not* a certified gameplay FPS delta.

| Numeric counter, 180 warm frames | Before network authority (WolfLinkReview) | After network authority (WolfNetMarch) | Observed after − before |
| --- | ---: | ---: | ---: |
| Mean FrameTime | 5.58739 ms | 5.56408 ms | **−0.02331ms** |
| Mean FrameTime-derived FPS-equivalent | 178.974 | 179.724 | **+0.750 equivalent** |
| Mean GPUTime | 5.28820 ms | 5.26875 ms | −0.01945ms |
| Mean `GPUMem/LocalUsedMB` | 711.929 MB | 714.932 MB | **+3.003 MB** |

BEFORE CSV SHA256 `408C64E64C0BFD22FA6FD9DF15EAF4AF82A122503B868535B469A800A70D22D8`; AFTER CSV SHA256 `5D9B745E712ADD4865BF52B4801B0E7DE44FAE598787EE3F057C1CCC5D2604D8`. Actual local pair analysis `wolf_net_march_perf_pair_verified.json` SHA256 **`262B245F6345530D1E7FBB36EF0548F5F112D7326C61BF41820E4EB4752A8A44`**. Benchmark measures *single-player paused developer scene* and **does not profile active two-client movement/combat GPU workload**. The apparent improvement is smaller than reasonable run-to-run uncertainty, so **NO performance gain is certified**.

## 6. Safe generated staging cleanup

After the final Cook, inspected `InputReviewProject\Saved\StagedBuilds\Windows`: **47 files / 885,552,841 bytes**, exactly identical by relative path, size and SHA256 to latest retained `PackageReview_WolfNetMarch\Windows`. Removed only that redundant regenerated folder. Actual separate incremental disk recovery **0.825 GiB**, local audit `cleanup_wolf_net_march_staging_20261121.json` SHA256 `0F64F78047C2683233AC7B40BB06A8710A35C6421460F0CD9AD82C1DCF7214AB`. **Final C: free = ~39.844 GiB**, because build/cook/cache and the new archive consumed space; do not sum deleted staging bytes as a net gain from the beginning of the entire ANIM-024 task.

## 7. Remaining blockers, risk, rollback

- True client **Interact** RPC must be invoked through player input and server-gate validation (security code reviewed/tested/compiled, but **actual click/button test NOT run**).
- Gameplay state/SaveGame migration, game-appropriate companion ownership across up to 8 players, choosing which Hero Wolf follows, deterministic movement across normal maps, animation Idle/Walk/Run/Foot IK and attack montage/notify/combat hit replication remain **NOT verified**. `bImmediateSmokeAttackImpact` remains an existing prototype behavior, not an approved combat animation.
- `Project.Maps.PIE` still reports **13 warnings** from missing presentation/UI icons, AR import, localization metadata and content reference issues. No new art assets and no 87-bone hero or ten exact production Montage paths included.
- Game `.umap`, Wolf V9 originals and many real source meshes are **untracked locally and absent from GitHub/LFS**. Do not merge this source-only PR as a playable map release; no source binary changes were committed to this PR.
- **Rollback:** remove/revert network authority and QA commits on **DRAFT** PR #110, restore the four files in isolated project from `netpatch_source_backups_20261121` and rebuild, or immediately run retained `PackageReview_WolfLinkReview`/prior `PackageReview_WolfAnimNative` without changing the live working tree. Preserve source audit and original screenshots/CSV. No changes merged into `main`.

**Decision: NETWORK STATE + MOVEMENT QA PASS (developer opt-in); FULL MULTIPLAYER GAMEPLAY/RELEASE QUALITY FAIL-CLOSED, PR #110 DRAFT/NOT MERGED.**

References: [Epic Actor property replication](https://dev.epicgames.com/documentation/en-us/unreal-engine/replicate-actor-properties-in-unreal-engine); [Epic networked Character Movement](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-networked-movement-in-the-character-movement-component-for-unreal-engine); [Epic Automation Tests](https://dev.epicgames.com/documentation/en-us/unreal-engine/run-automation-tests-in-unreal-engine).
