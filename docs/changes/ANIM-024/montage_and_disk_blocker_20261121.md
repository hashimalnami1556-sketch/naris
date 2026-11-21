# ANIM-024 — Read-only animation coverage and urgent storage blockade (2026-11-21)

**Latest decision: BLOCKED.** Windows device storage is critically low; do not run another full Cook/import/Blender render until disk space has been reviewed and explicitly authorized for cleanup. This report contains **no deletion instructions executed** and makes no claim of having created missing Montages.

## Actual UE Animation source inspection (read-only)

Unreal Engine 5.7.4 commandlet enumerated `/Game/NARIS/W04` on the isolated NARIS_W04 project and loaded **4 actual AnimMontages** and **42 selected AnimSequences** in `RigV3`, `WolfUnitsV8` and `WolfPresentationV9` source roots. Raw machine `C:\dev\NARIS_ANIM024_20261121\anim024_source_montage_feasibility.json` SHA256 `09B8CEE40AC61CE22AB13D9D7918BEBFC0939DB93EDD20FF8298FB61C0D1F34C`. This is a selected-path feasibility report; the previous full in-editor inventory found **78** AnimSequences across all W04 asset namespaces.

Four existing real Montages, all on `SK_CelestialWolf_UNITS_V8_Skeleton`, **not** at the exact ten production object paths:
- `AM_Wolf_Bite`: 0.1833 s
- `AM_Wolf_Dash`: 0.2833 s
- `AM_Wolf_Roar`: 0.4500 s
- `AM_Wolf_SoulVision`: 0.5833 s

Their `notifies` property was **protected and unreadable** via UE Python `get_editor_property('notifies')`; `slot_anim_tracks` wasn't available through the attempted API. Thus **do not claim 0 or 1 actual Notifies**, correct slot settings, `NarisWolfAttackImpactNotify`, NotifyState coverage, or gameplay validity from this read-only export.

### Ten exact W04 animation manifest entries — source feasibility

Source manifest: `unreal/NARIS_W04/Content/NARIS/W04/Animation/W04_AnimationBindings.json`.

| Required role | Existing candidate source sequence/montage | Status |
| --- | --- | --- |
| hero_light_attack | `AN_Ashen_Attack_Light` ~0.50s, AshenVessel V3 skeleton | **Candidate only**, production `AM_Hero_LightAttack` missing, required hit-window + impact Notifies unverified |
| hero_heavy_attack | `AN_Ashen_Attack_Heavy` ~0.70s | **Candidate only**, exact montage + required Notifies missing |
| hero_dodge | `AN_Ashen_Dodge` ~0.70s | Candidate source exists, montage missing |
| hero_parry | `AN_Ashen_Parry` ~0.567s | Candidate source exists, montage missing |
| celestial_wolf_attack | `AN_Wolf_Bite` and existing `AM_Wolf_Bite` on Wolf V8 skeleton | Candidate sources exist, exact role `AM_CelestialWolf_Attack` and impact notify verification missing |
| bone_beast_claw_sweep | `AN_Beast_Swipe` / `AN_Beast_TailSweep` | Candidate but exact `AM_BoneBeast_ClawSweep` missing, impact notify absent or unreadable |
| bone_beast_bone_charge | `AN_Beast_Run` exists | **Not proven authored charge**; using Run under a new combat name would fake a new animation |
| bone_beast_ash_rupture | `AN_Beast_Roar` or `AN_Beast_Enrage` exists | **No authored ash rupture clip verified**; do not invent one |
| bone_beast_phase_transition | `AN_Beast_Enrage` exists | Candidate concept only; phase-transition gameplay not proven |
| bone_beast_death | The seven actual Beast sequences are `Enrage`, `Idle`, `Roar`, `Run`, `Stunned`, `Swipe`, `TailSweep` | **No appropriately authored death clip verified**; DO NOT rename Stunned/Idle as Death |

**Hard gate:** 0/10 exact required manifest `AnimMontage` objects were loadable at prior local W04 paths. Existing sequence or differently named montage is not a compliant production combat asset. With untracked user art, production 87-bone skin failing stress and storage critical, no art/animation binary has been created or overwritten in this continuation.

## Windows storage: critical, actual measurement

The remote AsusRog `C:` filesystem reported **0.80 GiB available**, then **0.224 GiB** in a later read. UE ZenLocal logged repeated `PutCacheValues RPC ... Insufficient Storage (507)` during asset metadata/compression requests (commandlet itself still ended with an engine exit 0). **Do NOT infer no error simply because a Python commandlet printed Success**; cache writing failed. No source assets or project paths were cleaned/deleted.

Read-only on-disk inventory of bounded test directories:

| Source directory | Occupied |
| --- | ---: |
| `C:\dev\NARIS_ANIM024_20261121\PackageReview` — oldest duplicate archive | **0.822 GiB** |
| `...\PackageReview_AllMaps` — intermediate duplicate archive | **0.825 GiB** |
| `...\PackageReview_WolfAnimNative` — most recent archive | **0.825 GiB** |
| `...\InputReviewProject\Intermediate` | **4.458 GiB** |
| `...\InputReviewProject\Saved` | **1.039 GiB** |
| `...\InputReviewProject\Binaries` | **0.683 GiB** |
| `...\InputReviewProject\Content` | **0.137 GiB** |
| `%LOCALAPPDATA%\UnrealEngine\Common\Zen` | **0.283 GiB** |

These sizes are *occupied disk bytes* from traversing files (not how much space deletion would necessarily free due to hardlinks/compression). They overlap the same project workflow but **the whole user workstation was not exhaustively scanned**. Most promising initial cleanup candidates are only the two *older* archives in the **isolated test folder** (combined 1.647 GiB), and regenerable test `Intermediate` artifacts. **No deletion is authorized or performed**; source assets, original dirty checkout, original Blender/GLB/FBX rigs, newest packaged version and Git history are not candidates for automatic cleanup. Keep the raw log/source hashes and evidence. A carefully reviewed explicit approval is required before any deletion or bulk modification.

### Next ordered tasks once disk headroom is restored

1. Verify physical disk headroom / Zen cache behavior and no `507` errors; preserve evidence and baseline hashes.
2. Resolve upstream CHAR-001 G1L 87-bone skin deformation rejection before hero target replacement.
3. Acquire/author missing *authentic* production montage source clips, especially BoneBeast Death, Charge and AshRupture; validate provenance, Skeleton, notifies, duration/slot and combat windows, then import to actual required `/Game` paths.
4. Perform same-camera/seed visual before/after/diff and movement GIF, real editor build + full Cook, `Project.*` automation, server + two clients **combat** sync, profiler baseline and error scan.
5. Merge only after all real quality gates; **PR #110 remains DRAFT / DO NOT MERGE**.

**Rollback:** No mutation of original art. Delete nothing without approval. Source-only documentation can be reverted through this draft branch. References: [Epic Animation Montages](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine), [Epic derived-data cache](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-derived-data-cache-in-unreal-engine).
