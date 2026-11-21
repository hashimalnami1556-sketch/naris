# ANIM-024 — Bone Beast authoritative state and 2-client health replication, Unreal 5.7.4

**Date:** 2026-11-21. **Status:** PASS for the limited packaged multiplayer **server→two-clients health and encounter-start replication**; **NOT** a playable combat/Montage/quest-completion/SaveGame certification. All operations on isolated `C:\dev\NARIS_ANIM024_20261121\InputReviewProject`; GitHub source-only draft branch `feature/ANIM-024-source-coverage-gate`, PR #110 **DRAFT / unmerged**.

## Baseline, source-of-truth and risk

Read-only UE5.7.4 Editor audit of the existing `NARIS_BoneBeastBoss_0001` in `W04_Prototype_ANIM024_WolfButtonReview` confirmed **`replicates=True`**, **`replicate_movement=True`**, default dormant setting `DORM_AWAKE`, no encounter running and initial `CurrentHealth=0.0`. Thus the defect was **not** missing Actor-level replication flags. Original C++ fields `CurrentHealth`, `CurrentPhase`, `bEncounterActive`, and `bEncounterComplete` were **not declared Replicated**, and code paths `BeginPlay`, `Tick`, `ApplyDamageToEncounter`, `RequestAttack`, `CommitAttackImpact`, encounter/completion and other mutating methods did not guard `HasAuthority()`. Clients could read their local save and alter encounter state rather than only receiving server values.

Original project `W04_Prototype.umap` SHA256 **`2D6D4A2EA4118B41AD0D29EAE4526A78252395F6BAEDF1EBE0D2F11C07D52A81`**, previous two clones `WolfLinkReview` SHA **`3EE92BE6C800855BD5542E9B095066772CB7408FD779BE443E9BD32C7965B6C6`**, `WolfButtonReview` SHA **`EE98D7DA21305C29D0AAAA40FCDB8DA66375562FC9078DC1510F77D849DF929D`**; **all three unchanged through this stage**. No `.umap`/`.uasset`/model/skeleton/material binary asset committed or changed.

## TDD and minimal source changes

1. Created `tests/anim024/test_anim024_boss_network_authority.py` with 7 source contracts for health/phase/encounter replicated properties, server-only damage and saved state, simulated-client health, and explicitly opt-in non-shipping QA. **RED** [Source CI #129](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44903953515) (NARIS Validate was green).
2. Patched `BoneBeastBoss.h/.cpp`: four `DOREPLIFETIME` properties, `ReplicatedUsing` health/phase; server-only mutating Boss methods; clients cannot restore local defeat SaveGame state. `-NarisBossNetProbe` (only `#if !UE_BUILD_SHIPPING`) initializes **100 HP** and active encounter on the **server** and applies **18 damage at server elapsed 12 seconds** once. Does **not** autoattack, end encounter, mark quest completed or write SaveGame. Initial [GREEN source CI #130](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44904059274).
3. Real first packaged network test confirmed server HP **100→82**, clients `OnRep_CurrentHealth` **100 then 82**; client active state. The first independent proof script mistakenly compared regex tuple values to nested Python lists and flagged **one false negative**. It was fixed *without altering C++ or gameplay logs*, and separate proof `boss_health_network_gate_verified_v2.json` **PASS**, SHA256 **`05C875EB611B849DB59DE375F06832D16052BCDA24914FADA11550302DDD09CB`**. Preserve the original false-negative file for audit (never pretend the first validator passed).
4. Review uncovered an additional bug: `OnRep_CurrentHealth` initially emitted `DamageTaken` even for first full-HP replication, causing a **fake hit effect** when clients joined. Also client-local ArenaController would not receive Boss `EncounterStarted` or `EncounterReset` events solely through raw bool replication.
5. Added two further **RED** tests [Source CI #131](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44904828265), then:
   - `BoneBeastBoss.h/.cpp`: transient nonreplicated sentinel `LastReplicatedHealth = -1.f`; only emit `DamageTaken` when health actually drops from a previously received health value. New `OnRep_EncounterActive()` emits `EncounterStarted` / `EncounterReset`; `OnRep_EncounterComplete()` emits `EncounterComplete`. Both bool properties use `ReplicatedUsing` and the source still `DOREPLIFETIME`s them.
   - `NarisBossArenaController.cpp` now handles `EncounterReset` by opening the local arena blocker. Actual visual doors must still be checked on a scene that **contains a BossArenaController Actor**; this small review map does not establish that.
   - Explicit non-shipping log `OnRep_CurrentHealth hp=... damagefx=0/1`, `OnRep_EncounterActive`, and encounter-complete trace without storing player data.
6. **Final [source CI #132 GREEN](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44904974135): 111 discovered / 109 passed / 2 previously skipped GLB integration cases / zero failed.** [NARIS Unreal Validate #?](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44904974200) **success**. This is code contract review, *not* a replacement for runtime network evidence.

Source changes confined to `unreal/NARIS_W04/Source/NARIS_W04/{Public/BoneBeastBoss.h,Private/BoneBeastBoss.cpp,Private/NarisBossArenaController.cpp}` and tests. Two stages of verified local rollback backups:
- `netpatch_boss_source_backups_20261121` (original two Boss source files), apply-audit SHA256 **`3C2AB06DCDB8475F6F29A2F7292D0C66A52251DBB87D9029187CD5C0796F3DE8`**.
- `boss_repnotify_prechange_source_20261121` (before second, 3-file RepNotify patch), apply-audit SHA256 **`D326A871C71BF332D30217A68A4A3D40DCD945EBA681FABF24C24BE916D73FD9`**.

## Real Unreal Engine 5.7.4 quality gate

| Actual gate | Outcome | Local audit SHA256 |
| --- | --- | --- |
| Final `Build.bat NARIS_W04 Win64 Development` | **PASS, exit 0** | `boss_notify_game_build.log` **`595C9DF9547A0B6C73BE9C5B51E1E75F32DAEC77AD4D313A63FC7C1F08E819AD`** |
| Final `RunUAT BuildCookRun -skipbuild -cook -stage -pak -archive` | **PASS, exit 0** | `boss_notify_buildcookrun.log` **`EB85F878FE80E1DAEEC8C258AE6A18321B6D2B0AE924A7691C568A823D2FF852`** |
| Initial final `Build.bat NARIS_W04Editor Win64 Development` | **BLOCKED, exit 6** while **different running Unreal project** `C:\Users\Admin\NARIS\NARIS.uproject` had active Live Coding. We did **not** close/kill it or change its settings | `boss_notify_editor_build.log` **`0F24FE5C66399FD8C9A7F97EE938911CC70F51A527A9D35F81EAB50C90127E92`** |
| Retried after the other user's Editor/Live Coding exited on its own | **FINAL Editor PASS, exit 0** | `boss_notify_editor_build_final.log` **`20552F02656A0E02C85B943FC10E2F6C564F929892512B5002F37E287241835A`** |
| Final **`Automation RunTests Project.*`** using freshly rebuilt editor | `Project.Maps.PIE` **Success**, **13 existing warnings / 0 errors / process exit 0** | `boss_notify_project_automation/index.json` **`B5EC9E9F8F5C6E27CA64595C99FDE898EF9CE6734DC17E5B50E9B6D7329EAF51`** |

New retained local review archive `C:\dev\NARIS_ANIM024_20261121\PackageReview_BossNetRepNotify\Windows`; **not** a published game, and **not** a production `.exe` release.

## Real packaged 1 listen server + 2 independent clients

All three use packaged Windows Development executables, real Unreal networking, loopback port **17938**, `-nullrhi -NarisSkipFrontEnd -NarisBossNetProbe`. No gameplay SaveGame or complete/death path, no client-side damage requested. Initial source-only health QA before the fake-effect patch had already proven sync; final runtime then verified:

| Real log outcome | Listen server | Client 1 | Client 2 |
| --- | --- | --- | --- |
| joined/welcomed | Two `Join succeeded` | Welcomed | Welcomed |
| start HP and active state | `100.00`, active=1, complete=0 | initial `OnRep_CurrentHealth hp=100.00 damagefx=0` + `OnRep_EncounterActive active=1` | Same |
| single server QA damage | `ServerDamage authority=1 before=100.00 after=82.00` exactly once | **no ServerDamage** | **no ServerDamage** |
| subsequent HP | `82.00`, active=1, complete=0, phase=0 | `OnRep_CurrentHealth hp=82.00 damagefx=1`; subsequent `Tick hp=82` | Same |
| network fatal/UE error matching | 0 | 0 | 0 |

**Independent final 16-check parser `boss_notify_network_gate_verified.json`: PASS**, SHA256 **`F0ECEA30980BF9ABD25CFF59ECC728CC183CBE0FE9C4711464218B575AA62C47`**. Full raw log SHA256 server **`425E01ECBAFA0FECE86B46D2A7234B30957549300370857781095584CBAD6D3C`**; client1 **`3DECF45B1EB3F11DF0AF621F1D8E69F5E50DBB8FE6EDDBA042B8997A9179EB3B`**; client2 **`4E332FE6DD4EE533151BA31B22380CE02FEB94B3A6B488B0914D559255D1AFA4`**. The borrowed Wolf-oriented launch harness's generic flags `movement_replication_verified=false`/`combat_replication_verified=false` are **not** pass/fail measures of this **Boss HP test**; do not treat them as combat failure or as combat proof.

**Test limitation:** `ApplyDamageToEncounter(18)` was called by a non-shipping server-only scheduled *QA command*. This **did not exercise** actual Wolf `RequestAttack` → Montage → `NarisWolfAttackImpactNotify` → `CommitAttackImpact`, collision/hitboxes, AI, boss melee output, real quest prerequisites, encounter completion/death, SaveGame migration, controller/keyboard input, or visually observed local arena blockers. Those remain open. Other actor/animation assets still missing from source control.

## Before/after/diff, actual numerical performance and storage

Real packaged D3D12 `HighResShot 1920x1080`, same `W04_Prototype_ANIM024_WolfButtonReview` map and `BugItGo 1100 0 180 -10 0 0` camera, before vs after code change **byte-identical** screenshots, both SHA256 **`0A1720D2DF521D720A38C927363826805D1FFDAAD104706E65921845E486817E`**; side-by-side `boss_notify_before_after.png` SHA **`98B64084D5EFD4E7216486A5DB1E700928BD7025DB9122E72622AA7AA8B35796`**; diff PNG all zero, SHA256 **`0F52608DD021E7069EF19F9D8F46F6D651AAF5CBAC5154465092DE3574CF8514`**. This validates **one static frame's unchanged rendering only**, not active animated GPU gameplay, a 3–5s action GIF or new artwork.

**Real single-pass D3D12 development map benchmark, exactly same map/camera, 240 CSV frames each, first 60 excluded:**

| Counter (180 analyzed frames) | Before Boss authority/RepNotify | After | Observational Δ |
| --- | ---: | ---: | ---: |
| Mean FrameTime | 5.66648 ms | 5.57645 ms | **−0.09003 ms** |
| `1000/mean(FrameTime)` FPS-equivalent | 176.476 | 179.326 | **+2.850 equivalent** |
| Mean GPUTime | 5.28366 ms | 5.26989 ms | −0.01377 ms |
| Mean `GPUMem/LocalUsedMB` | 714.682 MB | 713.926 MB | −0.756 MB |

Baseline CSV SHA256 `4159A36B63999268EC15FF0F64E4EC4A24033CEBDFaf2841e6bbb36b9281fcde`, after CSV SHA256 `171DA607A9DB24A05B620799C55C9EE8FD72FC034E51DEDCCADED5EC755FB31D`, pair report `boss_notify_perf_pair_verified.json` SHA256 **`61BF3F3620ED7DBA5529FF2535FF70E818B328DD14083CB922BF0784DD95461A`**. **Neither +2.85 represents actual player FPS improvement nor is a certified perf change**: static menu-paused developer level, only 1 trial each, physical framebuffer/Seed/animation phase/background load not certified; no 2-client D3D12 boss combat. Production FPS and memory budgets remain OPEN.

After Cook, generated staging `InputReviewProject\Saved\StagedBuilds\Windows` contained **47 files / 885,593,797 bytes**, all SHA256-identical by exact relative path and size to **retained** `PackageReview_BossNetRepNotify\Windows`. Removed **only that redundant temporary staging copy**, freeing **0.825 GiB in that pass**, keeping previous and latest archives, original source models, logs and user canonical checkout. Audit SHA256 **`A555A76983DC2B7B471C90A971B91491CFD43B7FBF7DEBFE0A5A1CC8387FAD39`**; subsequent C: free ≈**28.266 GiB** (after newer packages created; not a total task net gain).

## Rollback and release decision

- Revert Boss source/arena source commits on **draft** PR only (do not merge current draft).
- Restore 3 original isolated C++ files from `boss_repnotify_prechange_source_20261121` for last prior good QA behavior, or both original Boss C++ files from `netpatch_boss_source_backups_20261121` to remove all Boss network additions; rebuild. Run archived `PackageReview_BossNetHealth` (prior real health sync) or `PackageReview_WolfButtonPositive` (prior source state) if rollback needed. No destructive asset operations.
- **Network authority / replicated Boss HP / no fake initial hit effect / initial encounter state:** verified developer subset. **Production gate still FAIL-CLOSED** until actual Wolf/Boss Montage/Notify hit, positive quest bond, SaveGame migration, multi-player group ownership, arena blocker visual runtime, 13 existing content warnings, full target hardware FPS/RAM/VRAM and complete assets pass.

References: [Epic Replicated Properties](https://dev.epicgames.com/documentation/en-us/unreal-engine/replicate-actor-properties-in-unreal-engine), [Epic RPCs](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine), [Epic Multiplayer Game Docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-and-multiplayer-in-unreal-engine).
