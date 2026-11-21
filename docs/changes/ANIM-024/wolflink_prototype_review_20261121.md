# ANIM-024 — Prototype Wolf mesh/ABP link: actual Unreal before → after (2026-11-21)

**Change:** visual/native binding of an existing original Celestial Wolf asset into a **NEW ISOLATED REVIEW MAP**. This is not a replacement or modification of the user's original W04 map, live GitHub `.umap`, production actor, or 87-bone hero rig. All UE binary source assets and PNG/CSV evidence are **LOCAL ONLY** to AsusRog.

## 1. Verified root cause and baseline

Read-only `EditorActorSubsystem` inventory of original isolated `/Game/NARIS/W04/Maps/W04_Prototype`:
- `NARIS_CelestialWolf_0001` is a real `ACelestialWolf : ACharacter` actor at world **(1800,0,100)cm**, but its `SkeletalMeshComponent.skeletal_mesh_asset=None` and `anim_class=None`.
- `NARIS_BoneBeastBoss_0001` also has no assigned skeletal mesh or AnimClass. **BoneBeast not touched** in this change; no invented asset replacement.
- Reference `W04_WolfPresentationV9_Review` uses real `SK_CelestialWolf_PRESENTATION_V9` and valid `ABP_CelestialWolf_C` on the same Actor class. Reference mesh relative transform: **Location (0,0,-90.15)cm, Rotation roll=0/pitch=0/yaw=90°, Scale (1,1,1)**.
- Isolated original `W04_Prototype.umap` SHA256 before AND after **`2D6D4A2EA4118B41AD0D29EAE4526A78252395F6BAEDF1EBE0D2F11C07D52A81`**. Original map snapshot retained `W04_Prototype_original_before_wolflink.umap` on AsusRog.
- BEFORE image real packaged D3D12 `HighResShot 1920x1080` from fixed `BugItGo 1100 0 180 -10 0 0`: `wolf_prototype_before_assetlink.png` SHA256 **`58D48ED563FC7AE664208ADB931D132040BDB4A8D9C15AAC5F425BCF7C1DA292`**. The gray prototype floor/black sky are visible, wolf missing.

## 2. Isolated asset change and safeguard

- Duplicated `W04_Prototype` to **`/Game/NARIS/W04/Maps/W04_Prototype_ANIM024_WolfLinkReview`**, then assigned the existing Wolf V9 SkeletalMesh and already-built native-parent-correct `ABP_CelestialWolf_C` to the duplicate's `NARIS_CelestialWolf_0001`.
- Explicitly guarded `Actor.get_outermost()` to verify cloned actor belongs to `WolfLinkReview` package and not original source.
- Initially attempted to copy Unreal's live `relative_location` / `relative_rotation` proxy structs from a reference map that had already been unloaded; audit caught invalid values (e.g. 5e-315 / zero scale) and **rejected** that map state. Corrected with fresh typed `unreal.Vector` / `unreal.Rotator` using *numerically verified* original V9 values, then saved and reloaded clone. **Actual stored values after correction:** `location=(0,0,-90.15)`, `rotation=(0,0,90)`, `scale=(1,1,1)`, `transform_verified=true`, source original unchanged.
- Clone final `.umap` SHA256 **`3EE92BE6C800855BD5542E9B095066772CB7408FD779BE443E9BD32C7965B6C6`**. Local `wolflink_review_map_apply.json` and `wolflink_transform_corrected.json` verify the source/target object path and invariants.
- Temporary review `DefaultGame.ini` copied to `DefaultGame_before_wolflink_cook.ini` then one `+MapsToCook` entry added for the clone **only inside** `C:\dev\NARIS_ANIM024_20261121\InputReviewProject`. Config baseline SHA256 `CD8148FEA0710604D26CC5BE78B5E75BE20A71A632C17B305989A5C8AFC1D35A`, isolated modified SHA256 `0D5211A11EC69142A3EF09CA49903487C08B240F897773C8587479FFCE0F1ACC`.
- **Do not commit** the single cloned `.umap` into GitHub or canonical repo until original `WolfPresentationV9` binary assets/asset provenance/required LFS are imported and reviewed. No current exact production `AnimMontage` path achieved.

## 3. Real after image and computed diff

- AFTER actual packaged D3D12 image from exactly the **same** camera command, 1920×1080 `wolf_prototype_after_assetlink.png` SHA256 **`5031EACDB6DF258808C99CD0EB00F33AE2D187BE457ED1A00698FFCBAB3CCEA2`**: the dark original Wolf model is visibly present in the developer floor where it was absent before. Ground/black sky are unchanged, **not** an environment-art improvement.
- Side-by-side `wolf_prototype_before_after.png` SHA256 **`04CD0D4D163FEC4383434D2917DBA868ADF96D2463E5E56CA55FEB9167921D4B`**.
- Pixel difference `wolf_prototype_diff.png` SHA256 **`E8283710029A3D684C756373CFDFE3C27C079E58F91D7342FA0E29A9EFB239A7`**. Changed-pixel bbox (pixel threshold 20): **(932,475,988,603)**, centered on rendered Wolf, and 4315 pixels changed in the measurement ROI. Local numeric report: `wolf_prototype_visual_comparison.json`.
- Seed, temporal animation frame and full viewport physical-resolution consistency remain **not independently proven**. Do not infer high-quality locomotion/IK from one static image.

## 4. Actual Win64 packaging and gameplay smoke gates

- **Real `RunUAT BuildCookRun`** with `-skipbuild -cook -stage -pak -archive` targeting the isolated 10-map project **exit 0, BUILD SUCCESSFUL**. Cook counted **510 total packages**, and the archive was created at **`C:\dev\NARIS_ANIM024_20261121\PackageReview_WolfLinkReview\Windows`**. UAT source log `wolflink_buildcookrun.log` SHA256 **`3E1EB8ED35B7BDC1E3B8FDD261199303A1C8065D7B38C7F493A22DABDAD41B75`**. New source C++ was unchanged from earlier successful Editor+Game Development builds; this round used existing compiled game binary plus newly cooked assets.
- Newly packaged clone launched using D3D12, produced screenshot and **exit 0**, no `Log.*Error` in capture output.
- **Real UE `Project.Maps.PIE` test** in current isolated project: `succeededWithWarnings=1`, `failed=0`, `notRun=0`, `warnings=13`, `errors=0`, editor automation process **exit 0**. Raw `wolflink_project_automation\index.json` SHA256 **`7E49135445352848A24652BC9F92FCB967B2BF58A648C532B73A773C2128444F`**; log SHA256 `7D6401DE412FB5724CC1B4AC64CB5C47334C8838A46B11E6BAD2E886D7297289`. PIE with 13 warnings is **not** a clean release gate.
- Packaged `127.0.0.1:17777` **one listen server + two `-nullrhi` clients**; server logged two `Join succeeded`, both clients logged `Welcomed by server (Level: ...WolfLinkReview)`. Loopback connectivity smoke only, **not** replicated Wolf movement/animation, combat hit authority or real multiplayer GPU performance. `wolflink_net_smoke_report.json` SHA256 **`107135C5B6C178D958BB780BE054DD5AF0ECCEB56EB272C1E27BCF932EE8B365`**. Harness stopped spawned game processes.

## 5. Real numeric before → after (developer map only)

Compared the *same camera* command and UE `-benchmark -seconds=30 -ExecCmds="BugItGo 1100 0 180 -10 0 0,csvprofile frames=240"` on the actual **old packaged original** vs **new packaged clone**. Each resulted in a real 240-frame CSV, engine exit 0, 180 warm frames after dropping first 60.

| Warm-frame CSV metric | Original W04_Prototype (no Wolf) | New cloned WolfLinkReview (Wolf bound) | Observed delta after − before |
| --- | ---: | ---: | ---: |
| `FrameTime` mean | **5.38737 ms** | **5.58739 ms** | **+0.20002 ms** |
| `FrameTime` p99 | 5.73096 ms | 6.43283 ms | +0.70187 ms |
| Derived `1000 / mean(FrameTime)` equivalent | 185.619 | 178.974 | **−6.645 FPS-equivalent** |
| GPUTime mean | 5.08903 ms | 5.28820 ms | **+0.19917 ms** |
| `GPUMem/LocalUsedMB` mean | 709.397 MB | 711.929 MB | **+2.532 MB** |

Both raw CSVs are **LOCAL ONLY**:
- BEFORE `PackageReview_WolfAnimNative\Windows\NARIS_W04\Saved\Profiling\CSV\Profile(20261121_090750).csv` SHA256 `728BB94115094D4D120DFD012A14593DAC8795648EE5318F81E69C15E72514B8`, 240 frames, 215 header columns and one appended dynamic custom column starting around frame 94.
- AFTER `PackageReview_WolfLinkReview\Windows\NARIS_W04\Saved\Profiling\CSV\Profile(20261121_090800).csv` SHA256 `408C64E64C0BFD22FA6FD9DF15EAF4AF82A122503B868535B469A800A70D22D8`, 240 frames, 227 columns.
- Local `wolf_link_perf_pair_verified.json` records actual parsed numbers. An early strict parser mistakenly treated valid UE late-appended custom counter as corrupted row; fixed via source regression gate [RED 104](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44874278735) then tool fix to accept **exactly one extra trailing counter**. More than one extra or missing numeric fields must still fail.

**Important:** these numbers reflect **one benchmark pass each** on tiny maps, unverified physical back-buffer resolution, unpinned random Seed/animation phase, potentially different PSO cache state, startup timing and background load. The `BugItGo` camera reposition produced `View/Speed2D` transient spikes (not continuous movement); warm 180 rows were used. **Do NOT call the observed ΔFPS a representative, reproducible production optimization or guaranteed 60fps game.** No active AI/combat/foot IK network profiling. The user-facing game build remains blocked despite successful visual proof.

## 6. Post-cook disk hygiene and rollback

- The new Cook generated `Saved\StagedBuilds\Windows`; all **47 staged files were verified identical by path, length and SHA256** to the new retained `PackageReview_WolfLinkReview\Windows`. Deleted only the redundant regenerated stage (885,451,001 byte entries / ~**0.825 GiB reclaimed**), audit `cleanup_wolflink_staged_duplicate_20261121.json`; retained new game executable and previous known-good package with original 240-frame CSV.
- Disk has ample remaining headroom (~39 GiB). No original source/character/rig assets deleted; old crash dump retained separately per [approved cleanup record](approved_isolated_cleanup_20261121.md).
- Rollback of this test change: do **not** promote this clone; restore isolated `DefaultGame.ini` from `DefaultGame_before_wolflink_cook.ini`, launch previously archived `PackageReview_WolfAnimNative`. Review-only cloned `.umap` and new archive may be archived or deleted later after verifying their evidence/provenance. **Never delete original `W04_Prototype.umap` or user-owned untracked Wolf assets**.
- Remaining blockers: wolf's authored animation playback/Idle→Walk→Run and hit notify synchronization not yet verified; BoneBeast in original prototype lacks visible SkeletalMesh and ABP; 87-bone hero candidate fails skin stress; 10 exact production montage paths missing; 13 PIE warnings (icons and AR/L10n), full AAA environment art and scalable 2-client combat perf not complete.

**Project status remains ANIM-024 DRAFT / NOT MERGED / NOT PRODUCTION.** This is a verified *isolated improvement* with real screenshots and tests, not an approved source-control integration.

References: [Epic Skeletal Mesh Assets](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-assets-in-unreal-engine); [Epic Animation Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprints-in-unreal-engine); [Epic Packaging](https://dev.epicgames.com/documentation/en-us/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine).
