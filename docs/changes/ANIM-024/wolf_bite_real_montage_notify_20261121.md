# ANIM-024 — Existing Wolf Bite Montage/Notify triggers real server damage and replicates to 2 clients

**Date:** 2026-11-21, **Unreal Engine 5.7.4**, **Win64 Development**, isolated `C:\dev\NARIS_ANIM024_20261121\InputReviewProject`. GitHub PR #110 still **DRAFT / UNMERGED**. **Scope:** a controlled non-shipping test of actual existing `AM_Wolf_Bite` montage → authored `NarisWolfAttackImpactNotify` → server-owned `ACelestialWolf::CommitAttackImpact` → `ABoneBeastBoss::ApplyDamageToEncounter` → replicated HP change. This is **more than** an instant test impact, but **not** remote client animation/visual sync, actual collision Hitbox, SaveGame, gamepad action or production release.

## 1. Why: avoid recreating real assets

Earlier [after-join real Wolf damage test](wolf_boss_real_attack_after_join_20261121.md) used existing `bImmediateSmokeAttackImpact=true`, immediately calling the production `CommitAttackImpact()` without relying on an Animation Montage or Notify. We therefore could not claim a timed real animation hit.

**Actual UE5.7.4 Editor read-only asset inspection in the local review project** found **four real `AnimMontage`** assets under `/Game/NARIS/W04/Characters/WolfPresentationV9/Combat/`: `AM_Wolf_Bite`, `AM_Wolf_Dash`, `AM_Wolf_Roar`, `AM_Wolf_SoulVision`, all with **DefaultSlot**, **Default** section and skeleton `/Game/NARIS/W04/Characters/WolfUnitsV8/SK_CelestialWolf_UNITS_V8_Skeleton`. The actual placed Wolf uses mesh `/Game/NARIS/W04/Characters/WolfPresentationV9/SK_CelestialWolf_PRESENTATION_V9` **with that exact same skeleton object**. Thus the V8-named skeleton does **not** imply a retarget mismatch for V9 Wolf; four Montages do **not** need to be regenerated. `AM_Wolf_Bite` has exactly **one** authored `NarisWolfAttackImpactNotify` at **0.0825s**, while the other three have **0** notify events. Read-only audits: `wolf_montage_readonly_preflight_20261121.json` SHA256 `40E4C83C08F4079E5378DDF02C96DBA62084DE8C0857C902ADA029DFFED28D49`, skeleton compatibility `04B40E7FA31500D52106D43BD73E510E2ABDE86FC8700D358798A8CA772FA9B7`, notify content `CA167FD6F17258652A3E3D568F6EEE3C61965D7A42CCDB0DBEA9DBC0BCFA3082`. These findings apply to **the isolated workstation asset package**, not proof all four binary Montages have been Git LFS tracked or supplied to every collaborator.

## 2. RED/GREEN source tests and narrow QA implementation

Added two source regressions in `tests/anim024/test_anim024_wolf_boss_combat_probe.py` requiring:
- explicit `!UE_BUILD_SHIPPING` `-NarisWolfNetProbeMontageOnce` disabling smoke impact, loading existing `AM_Wolf_Bite`, calling `UAnimInstance::Montage_Play`, logging missing animation/montage and refusing synthetic damage if play fails;
- the **authored real** `UNarisWolfAttackImpactNotify::Notify` then calling Wolf's server-only `CommitAttackImpact`.

[**RED Source Motion Coverage**](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44916413520) failed correctly before implementation. Source fixed `CelestialWolf.cpp` and added non-shipping notify provenance in `NarisWolfAttackImpactNotify.cpp`. One implementation initially failed a too-literal test assertion when disabling instant impact through the equivalent inverse-expression; adjusted source to explicit `if(OptInMontage){ bImmediateSmokeAttackImpact=false; }else{...=true;}` rather than bypassing the test. [**GREEN Source Motion Coverage**](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44916568288) **119 discovered / 117 passed / 2 pre-existing GLB skips / 0 failures**; [Unreal Validate](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44916568366) **PASS**.

**Non-shipping QA flags** on the isolated listen server only: `-NarisBossNetProbe -NarisBossNetProbeNoDamage -NarisWolfNetProbe -NarisWolfNetProbeCombatOnce -NarisWolfNetProbeMontageOnce`, with game `-NarisSkipFrontEnd`. The existing `TickAttack` waits for **2 real client connections and game time≥12s** under QA only, moves the Wolf, then `RequestAttack` calls `Montage_Play` on its existing active AnimInstance. **No instant-smoke damage** in this branch. The one authored Notify calls `CommitAttackImpact` after the montage actually advances. Existing server authority, range, active encounter and once-per-hit checks apply; Wolf then enters Guard. No `.uasset` modified or generated, original models untouched, no quest/death/SaveGame writing.

Before local isolated source writes, verified exact prior C++ against source staging/Git, hash-backed two files in `wolf_montage_prechange_20261121`; source audit `wolf_montage_source_apply_audit_20261121.json` SHA256 **`DFFE74AB3D16F9FB8673FB32947B898FE9E54C72075B209245CD9A4767A74E33`**. Rollback restores `CelestialWolf.cpp` and `NarisWolfAttackImpactNotify.cpp` from that directory and rebuilds, or runs prior known-good `PackageReview_WolfBossAttackAfterJoin`.

## 3. Mandatory Unreal build, PIE, live 2-client multiplayer test

| Real gate | Result | LOCAL proof SHA256 |
| --- | --- | --- |
| `Build.bat NARIS_W04Editor Win64 Development` | **PASS, exit 0** | `wolf_montage_editor_build.log` `FFB400475C7B7786A15204B4D033CD28D2145EFD53E0EC5520E135D34F654D69` |
| `Build.bat NARIS_W04 Win64 Development` | **PASS, exit 0** | `wolf_montage_game_build.log` `3451481610CDFD2E4BD2B2CE02F7D3384690C163C32065682A523B82813FE6ED` |
| `RunUAT BuildCookRun -skipbuild -cook -stage -pak -archive` | **PASS, exit 0** | `wolf_montage_buildcookrun.log` `61C96F985F9217A956EB49541D6E5BE915CF72B002F4283D0EB97EB5C5B95BF4` |
| `Automation RunTests Project.*` | **Project.Maps.PIE Success, 13 existing warnings / 0 errors, exit 0** | `wolf_real_montage_project_automation/index.json` `7775D02DBCD09B12DA6196ECF0D3AE32270B7EF3E7FFF6D7DB223730B9C032F9` |

**Real packaged listen server + two independent cooked Win64 Dev clients** on `127.0.0.1:17941`, `-nullrhi` each. Clients both successfully joined **before** server attack. Chronological server log:
1. `NARIS_WOLF_COMBAT_PROBE event=ServerMontagePlay authority=1 valid_asset=1 valid_anim_instance=1 duration=0.183` — **the real authored Bite montage loaded in the cooked package** and started on server.
2. `NARIS_WOLF_COMBAT_PROBE event=MontageNotify authority=1 anim=AM_Wolf_Bite` — authored notify fired after actual Montage playback.
3. `NARIS_WOLF_COMBAT_PROBE event=ServerWolfAttackImpact authority=1 before=100.00 after=82.00 damage=18.00` — **exactly one** hit, initiated only by Notify with immediate smoke disabled.
4. Client1 and client2 each had baseline `OnRep_CurrentHealth hp=100.00 damagefx=0`, then received real live `OnRep_CurrentHealth hp=82.00 damagefx=1`, `OnRep_Mode mode=1` (Guard). No client applied server damage; Boss remained active, complete=0, HP82.

Real strict **18/18 condition** network proof `wolf_real_montage_network_gate_verified.json` **PASS**, SHA256 **`027813CC5E70CD0A9A107AB97E6DE7F01FFCF0EF1E35A08C8771A5F3F62F9C14`**, including exact server order, client presence *before* montage, one notify/hit, authoritative-only impact, 2 client health changes and original+two review-map hashes unchanged. Raw network logs SHA256: server `5BBED62CDFAD0F5A5E2699A5BA2129BAEB5A2DEFDFFD969A6BFB980260DAC815`, client1 `1B73C29B34DB0FA09EC89406D4B8B9CB672121338D7116B72C50562977D2D1B7`, client2 `452F8F5238C0A11A7B83D2B3E7A64F800526D382771EC1BE40C5FC40104CAF02`. Only server had `-NarisWolfNetProbeMontageOnce`; **the clients did not play the Montage** in this test, so neither client animation visuals nor network animation timing is certified.

## 4. Before/after/diff, performance and safe storage

Actual packaged D3D12 `HighResShot 1920x1080` on same QA map, static `BugItGo 1100 0 180 -10 0 0`. Before (Wolf immediate smoke build) and after (real montage notify build) **byte-identical** screenshot SHA256 `0A1720D2DF521D720A38C927363826805D1FFDAAD104706E65921845E486817E`; `wolf_real_montage_before_after.png` SHA `98B64084D5EFD4E7216486A5DB9122E72622AA7AA8B35796`, black pixel diff `wolf_real_montage_diff.png` SHA `0F52608DD021E7069EF19F9D8F46F6D651AAF5CBAC5154465092DE3574CF8514`. **Static screenshot only**; animated moving attack and actual client GPU visuals not depicted.

**Valid, but only observational, D3D12 DEV A/B** same QA map, fixed requested camera, 240 frames each; 60 startup frames excluded and **180 analyzed** per file. The earlier Wolf *immediate-smoke* benchmark CSV was **rejected** as variable-width; for this comparison we use a different **valid 240-row earlier Boss Net RepNotify DEV benchmark**, which predates Wolf one-shot instant code. It is a baseline for *combined later source QA*, **not** an isolated Montage-versus-smoke cost.

| Static Dev counter | Earlier same-map Boss RepNotify source | After real montage QA source | Observational Δ |
| --- | ---: | ---: | ---: |
| FrameTime mean | 5.57645ms | 5.73375ms | **+0.15730ms** |
| FPS-equivalent `1000/mean(FrameTime)` | 179.326 | 174.406 | **−4.920 equivalent** |
| GPUTime mean | 5.26989ms | 5.35972ms | +0.08983ms |
| GPU local-used mean | 713.926MB | 711.386MB | −2.540MB |

After CSV was **uniform-width** (223 columns) and contained **240 frame rows**, unlike previous malformed CSV. Baseline CSV SHA `171DA607A9DB24A05B620799C55C9EE8FD72FC034E51DEDCCADED5EC755FB31D`, after CSV SHA `95A949B80E07E161F4BF5AE246471A0BD6553AF75DA3BFED4702C075C7DC07B7`, strict `wolf_real_montage_perf_pair_verified.json` SHA256 `57EA96E3F0F684973C0EE4B1917E8CBC3A8293CF5F246F6200B80889CBE6494B`. **One-pass static Dev scene**, actual backbuffer/Seed/animation time/background load not proven; **FPS gain/regression and min-spec budgets NOT certified**, no D3D12 2-client active combat benchmark.

After Cook, 47 staged files **885,596,485 bytes** compared with retained current `PackageReview_WolfRealMontageNotify\Windows` by exact path, length and SHA256, all identical. Removed **only duplicate generated staging copy**, recovered ~**0.825GiB** this pass, kept current and all prior archives, source user art and Git main untouched. Audit `cleanup_wolf_real_montage_staging_20261121.json` SHA256 `57849A63DF0A8E8EA1E778355EA0A76B1B00C4D999933333199252896EF6BC1F`. Free C: ~**25.421GiB** after separate builds/archives; not net total savings. No orphan NARIS_W04 QA game processes.

## Remaining production gates / decision

**PROVEN:** authored Bite Montage on server → authored impact Notify → exactly one actual authoritative damage → 2 real clients updated live, no initial false hit, no Game/Editor/Cook/PIE failures. **NOT PROVEN:** both clients actually *render* the Bite montage or process synchronized animation timing, hitbox/contact geometry, asset/LFS availability on other workstations, full quest bonding and SaveGame migration, 8 clients, gamepad controls, 87-bone production hero, ten expected production Montages across other characters, localization/UI warnings, representative GPU/min-spec FPS. Thus PR #110 **must remain DRAFT / NO MERGE**.

Refs: [Epic Animation Montage](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine), [Epic Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine), [Epic Actor Replication](https://dev.epicgames.com/documentation/en-us/unreal-engine/replicate-actor-properties-in-unreal-engine).
