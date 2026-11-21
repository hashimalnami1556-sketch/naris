# ANIM-024 — Positive *Interact()* method route verified with 2 clients (2026-11-21)

**Actual milestone:** Using a real Windows Unreal Engine **5.7.4 Development** game and a NEW isolated development-only duplicated map, one remote client called the same `ANarisHeroCharacter::Interact()` method bound to the gameplay input action. The server **accepted** the resulting player-owned Hero RPC's Wolf target as valid/in range and both clients received the follow-up replicated Mode=Guard. This is **not hardware keyboard/gamepad input evidence and not the actual quest unlock/SaveGame**: this explicit test uses `-NarisWolfNetProbeNoSave` to return before persistent game mutation.

## 1. Before — source and geometry

Prior [remote client RPC review](wolf_client_owned_rpc_live_20261121.md) on original cloned `W04_Prototype_ANIM024_WolfLinkReview` (with PlayerStart **(-400,0,100)cm**) proved a forged direct `ServerInteractWithWolf` target was **rejected** by the server, but lacked a *positive* near-range test and never invoked the real `ANarisHeroCharacter::Interact()` method. Existing Wolf in that map is at **(1800,0,100)cm**, **2200 cm** from PlayerStart; the 220cm interaction limit is smaller.

Read-only Unreal editor inventory confirmed the original debug map has one each of:
- `PlayerStart=(-400,0,100)`;
- `NARIS_Waystone_0001=(0,0,50)`;
- `NARIS_MemoryCrystal_0001=(600,0,50)`;
- `NARIS_AshGate_0001=(1200,0,100)`;
- `NARIS_CelestialWolf_0001=(1800,0,100)`;
- `NARIS_BoneBeastBoss_0001=(3000,0,100)`.

No production SkeletalMesh/Animation asset change was needed to test positive target ownership/range. The Wolf is the same existing V9 mesh and `ABP_CelestialWolf_C`.

## 2. TDD and isolated map creation

First added a RED source contract requiring an opt-in, **non-shipping** `-NarisWolfNetProbeInputButton` to call the actual `Interact()` method from client Hero `Tick` after possession; not just the lower-level `ServerInteractWithWolf` RPC. [Source Motion Coverage run #127 RED](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44902914178) confirmed the absent behavior. Then modified **only** `NarisHeroCharacter.cpp` under existing `#if !UE_BUILD_SHIPPING`: if this flag is specified, emit `ClientInteractButton`, call `Interact()`; otherwise keep previous direct RPC probe. No real hardware key event is synthesized. [Source Motion Coverage run #128 GREEN](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44903040254): **102 discovered / 100 passed / 2 pre-existing GLB integration skips / 0 failures**; [Unreal Validate run](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44903040233) PASS.

Before altering local isolated UE source, checked exact previous QA source against SHA-verified staging, backed up `NarisHeroCharacter.cpp` to `netpatch_hero_input_before_button.cpp` (SHA256 before **`4D081BAD4FED1093E99AE901CF9CB0A27C78997C965C0F8FCF86D4FA9632DE9A`**) and separately backed up `Config/DefaultGame.ini` to `DefaultGame_before_wolf_button_cook.ini` (SHA256 before **`0D5211A11EC69142A3EF09CA49903487C08B240F897773C8587479FFCE0F1ACC`**). After patch: local `Hero.cpp` SHA256 **`C4B3C888228F3ACB31D990CEF283597AFE4C9A569E4277CDE6974C0C9208E176`**; isolated Config SHA256 **`3039D9610E7952C9458786DCF323BEB00DABCADC03819144E8857FA898CE75A7`**, having **one additional** `MapsToCook` entry for the newly cloned QA map.

**Create fresh map only, no master overwrite:** duplicated prior `/Game/NARIS/W04/Maps/W04_Prototype_ANIM024_WolfLinkReview` → `/Game/NARIS/W04/Maps/W04_Prototype_ANIM024_WolfButtonReview` and moved *only that new map's PlayerStart* from **x=−400cm** to **x=1650cm**, **150cm from Wolf at x=1800cm**. Saved and re-opened to verify exact new coordinates, original map SHA preserved, existing Wolf mesh/ABP unchanged. Local map creation report `wolf_button_positive_review_map_create.json` SHA256 **`9E7492D581AF17E0B2CDDA93F66C5ED95F22D8CBFFE0BF5B8CA85DEC3A3AE8F8`**. Map hashes:
- Untouched original `W04_Prototype.umap`: SHA256 **`2D6D4A2EA4118B41AD0D29EAE4526A78252395F6BAEDF1EBE0D2F11C07D52A81`**.
- Untouched previous WolfLink clone: SHA256 **`3EE92BE6C800855BD5542E9B095066772CB7408FD779BE443E9BD32C7965B6C6`**.
- NEW WolfButton QA clone only: SHA256 **`EE98D7DA21305C29D0AAAA40FCDB8DA66375562FC9078DC1510F77D849DF929D`**. Original master dirty/untracked user's assets were not modified.

## 3. Actual packaged Win64 builds, Cook and PIE

| QA gate | Verified result | LOCAL evidence SHA256 |
| --- | --- | --- |
| `Build.bat NARIS_W04Editor Win64 Development` | **PASS, exit 0** | `wolf_button_editor_build.log` **`AFA6DEE818E7E547031E73D6EA9EEA2A96433BA25B20713049FFE0D2C3021150`** |
| `Build.bat NARIS_W04 Win64 Development` | **PASS, exit 0** | `wolf_button_game_build.log` **`104EC0B686F88F44FC126A11F07CBEE8CD9F84801F1A1F20335C059010443B27`** |
| `RunUAT BuildCookRun -skipbuild -cook -stage -pak -archive` | **PASS, exit 0**, includes newly duplicated map | `wolf_button_buildcookrun.log` **`128C47F8DD5DF990507970A0505E3C9CE53360AEFE870B402569146CB39C157D`** |
| `Automation RunTests Project.*` | **Project.Maps.PIE Success, 13 old warnings, 0 errors, exit 0** | `wolf_button_positive_automation/index.json` **`19A949E3BF45EFF27C8AF16A18FF748ACA3FC8719B0E10DED097919DD101EA92`** |

**New packaged archive kept local:** `C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfButtonPositive\Windows` (not uploaded to GitHub). Prior archive(s) remain the rollback path.

## 4. Actual one listen server + two-client POSITIVE input method test

All are real packaged Unreal Dev processes, using loopback **127.0.0.1:17935**, `-nullrhi -NarisSkipFrontEnd -NarisWolfNetProbe`. **Server only:** `-NarisWolfNetProbeFollow -NarisWolfNetProbeNoSave`, so bBonded starts in QA mode, and even a valid test interaction returns before the real quest/SaveGame path. **Client1 only:** `-NarisWolfNetProbeInput -NarisWolfNetProbeInputButton`; client2 receives no input QA flags. Never run this exact test outside the isolated disposable review world/server.

**Observed actual logs, in order:**
1. Server logged **two `Join succeeded`**; clients welcomed and received `OnRep_Mode mode=0` (Follow), `OnRep_Bonded bonded=1`.
2. Client1 emitted **`NARIS_WOLF_NET_PROBE event=ClientInteractButton authority=0`**, then actually called `ANarisHeroCharacter::Interact()`, which used its nearest-in-range Wolf and the player-owned `ServerInteractWithWolf` RPC.
3. Server emitted **`event=ServerInteractAccepted authority=1`**. In the new map, server accepted the client's wolf target as its nearest interactable within **220cm**. No `ServerInteractRejected` event occurred. This proves the *range/target/ownership route*, not quest-gate success or new save writes.
4. Client1 emitted `ClientCycleMode authority=0`; server emitted `ServerCycleMode authority=1`; **both clients** received **`OnRep_Mode mode=1`** (Guard).
5. **0** Unreal fatal/network error matches in all 3 harness logs. Active network movement was **not** tested in this trial (server Wolf was already 150cm from PlayerStart, within Follow acceptance radius), and no combat or attack animation was triggered.

A separate strict **14-check** post-test validator `wolf_button_positive_gate_verified.json` reports **`gate_pass=true`**, SHA256 **`A78D49908F899755AA715EEAC18975314906025B8AE666D4DB15DED67AA9BC3A`**. Raw `wolf_button_positive_report.json` SHA256 **`DA038A18F65EF279EB87174310BAFC4CEB3618DB7DABB54E7E51437BF10AADBD`**, server log **`B6423A3B355313963C99581C16DE69FE53C872C51B0FDFED414C3210D3628597`**, client1 **`85E96DB689D5A2E2E92B6CFC9A56EB6E478188FD3BE6998B336244F3BE3724A1`**, client2 **`FB21DA8D16624DFA9F514E31AB9E8FD96449A0BCBE28A08D19FDC471BD2303BD`**. Post-test checks found no `Saved/SaveGames` directories in isolated game source, packaged game, or `%LOCALAPPDATA%\NARIS_W04\Saved\SaveGames`; only these scoped paths were checked.

**Precise boundary:** the client `Interact()` method was **QA-triggered on one tick**, not real keyboard/controller hardware. The server `-NarisWolfNetProbeNoSave` deliberately prevented executing `Interaction->Interact()` after acceptance, so **the game's actual `BondWithPlayer`, required gate, quest step, persistence/migration, load/reload and ownership among 8 players remain UNVERIFIED**. Only actual valid target/owner-routing + RPC acceptance and replicated mode are supported.

## 5. Real screenshot before/after/diff and after-map performance

- Real packaged D3D12 after `HighResShot 1920x1080` `BugItGo 1100 0 180 -10 0 0` with new WolfButton map, SHA256 **`0A1720D2DF521D720A38C927363826805D1FFDAAD104706E65921845E486817E`**. Previous WolfLink map screenshot SHA256 **`5031EACDB6DF258808C99CD0EB00F33AE2D187BE457ED1A00698FFCBAB3CCEA2`**. Actual side-by-side `wolf_button_positive_before_after.png` SHA256 **`AB784E982AB0EB321F4C2E1792DC1987A3E75B58C5E0C61C9287D43182CBECB4`**; highlighted pixel diff `wolf_button_positive_diff.png` SHA256 **`B5899BE5BF5C03749C54CDDC7D1B490CD919F32F345C385B00A9EBC6F405A105`**. Unlike prior same-map source-only checks, here the after image differs, with diff bbox **(0,395,1920,1080)**; **do not call it identical**. The test map's spawn/camera setup is intentionally different, no new environment art or wolf skin was created.
- **Actual 240-frame, single-player D3D12 static DEV scene** after 60 warmup frames, `-benchmark -ExecCmds="BugItGo...,csvprofile frames=240"`: new WolfButton map **FrameTime mean 5.66648ms**, p95 **6.01942ms**, p99 **6.75630ms**, derived FPS-equivalent **176.476**, GPUTime mean **5.28366ms**, GPU local used mean **714.682MB**. Raw current CSV SHA256 **`4159A36B63999268EC15FF0F64E4EC4A24033CEBDFaf2841e6bbb36b9281fcde`** (case-insensitive). 
- Earlier WolfLink original spawn -400cm DEV map was FrameTime mean **5.57992ms**, derived equivalent 179.214 and GPU local used 711.951MB. **Numeric apparent delta +0.08656ms / −2.738 FPS-equivalent / +2.731MB is NOT a controlled or causally comparable before/after**, because the maps differ (PlayerStart -400 →1650, resulting camera/session geometry and initial conditions differ), as well as one-pass background, unstabilized random Seed/animation, and physical framebuffer not independently verified. Therefore official **`ΔFPS` / `ΔVRAM` = N/A**, production FPS remains **UNVERIFIED**. Local numeric `wolf_button_positive_perf_pair_verified.json` SHA256 **`A2EE92B28323FEC15F585CDC611892FEF64EADAF4D02F4C19F15C12C301D4075`**.

## 6. Storage and rollback

- After Cook, `InputReviewProject\Saved\StagedBuilds\Windows` had **47 files, 885,570,117 bytes**, all matching by relative path, length and SHA256 in retained `PackageReview_WolfButtonPositive\Windows`. Removed only that hash-verified temporary duplicate, not the new archive, older archives or `Saved\Cooked`. Incremental local space gain from this operation **0.825GiB**. Audit `cleanup_wolf_button_positive_staging_20261121.json` SHA256 **`0A6197F05055C3001F1213151CF4C3C042ADA150583BE461370B6D78FEA16009`**. Final free disk ~**35.397GiB** after retaining new package and build artifacts. Do not treat gross duplicate deletion as total task net capacity gain.
- **Rollback:** restore source `NarisHeroCharacter.cpp` from `netpatch_hero_input_before_button.cpp` (matched source SHA **`4D081BAD...`**), restore isolated `Config/DefaultGame.ini` from `DefaultGame_before_wolf_button_cook.ini` (SHA **`0D5211A1...`**), rebuild. To instantly run last known-good previous client-owned RPC, launch retained `PackageReview_WolfClientCommands` or `PackageReview_WolfNetMarch`. The new WolfButton QA map may be retained for subsequent test or archived; no canonical source `.umap` or original Art/Animation source was edited.

**Conclusion: real client-origin `Interact()` method → server valid target acceptance, then mode replication to two clients PASS on isolated WolfButton test map; true quest bond/SaveGame, hardware input, attack hit authority/animation and full art/perf remain OPEN; PR #110 DRAFT / NO MERGE.**

References: [Epic RPCs](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine), [Epic Actor Ownership](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-owner-and-owning-connection-in-unreal-engine), [Epic networked movement](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-networked-movement-in-the-character-movement-component-for-unreal-engine).
