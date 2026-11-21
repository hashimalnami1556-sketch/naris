# ANIM-024 — UE5.7.4: map cooking, wolf camera evidence, and native AnimBlueprint repair (2026-11-21)

**Change state:** review-only local UE integration, **NOT production-approved**; PR #110 remains **DRAFT / NO MERGE**. This document distinguishes asset presence from shipping inclusion, class loading from gameplay animation, and camera framing from actual model improvement.

## 1. Reproducible test environment

- Actual remote test machine: `AsusRog`, Windows, Unreal Editor **5.7.4**.
- Local original checkout: `C:\dev\NARIS_ENV020_20261114\unreal\NARIS_W04`, on **detached HEAD**, with many **untracked `.uasset` and `.umap`**. **Do not reset, clean, overwrite or bulk-commit original user assets**. An Unreal launch changed original `Config/DefaultInput.ini` in prior testing; no original asset byte-preservation claims are made beyond documented snapshots.
- Test project (full independent copy): `C:\dev\NARIS_ANIM024_20261121\InputReviewProject`. Art, maps, generated binary and all supporting logs stay LOCAL to this device. The GitHub branch does **not** contain those untracked map/asset packages.
- Baseline review archive: `PackageReview\Windows`; nine-map trial archive: `PackageReview_AllMaps\Windows`. Do not mistake either for a released build.
- Pixel capture: actual packaged **D3D12 RHI**, 1920×1080 `HighResShot`, not `-nullrhi`.

## 2. Missing packaged maps: red → green

**RED:** `W04_AshenForest_Blockout` and `W04_WolfPresentationV9_Review` existed as `.umap` files and were reported by real UE AssetRegistry but their packaged executable rejected them with `Failed to load package`. The only configured map was `W04_Prototype`; other nine maps were not listed for cooking.

**Isolated change only:** after backup of `InputReviewProject\Config\DefaultGame.ini` to `C:\dev\NARIS_ANIM024_20261121\DefaultGame_before_mapcook.ini`, add all **9 existing local W04 maps** via `+MapsToCook=(FilePath="/Game/NARIS/W04/Maps/<map>")` under `[/Script/UnrealEd.ProjectPackagingSettings]`. Original config SHA256 **FD7A18805C793EBE1FA11E3B6D3F69D381BAA60774E04A20590FBCB0201514D3**, isolated modified config SHA256 **CD8148FEA0710604D26CC5BE78B5E75BE20A71A632C17B305989A5C8AFC1D35A**. No `.umap` modifications performed.

Nine local map names: `W04_AshenForest_Blockout`, `W04_Prototype`, `W04_WolfGround_Review`, `W04_WolfLocomotion_Review`, `W04_WolfNormalsV7_Review`, `W04_WolfPresentationV9_Review`, `W04_WolfStanceV5_Review`, `W04_WolfStanceV6_Review`, `W04_WolfUnitsV8_Review`.

**GREEN:** real `RunUAT BuildCookRun -noP4 -platform=Win64 -clientconfig=Development -skipbuild -cook -stage -pak -archive` returned **`BUILD SUCCESSFUL` / ExitCode 0**. `allmaps_buildcookrun.log` SHA256 **605775F2CE0F620D07363F78DA7825AA3F79FFF838479BC45AC5D330BCF51A3D**. Nine-map archive has **52 files, ~844.37 MB**. Packaged executable `Load map complete` confirmed for both previously missing maps, screen image files actually generated. `W04_AshenForest_Blockout` capture harness terminated after timeout (process exit observed as -1); this **is not** an unconditional successful gameplay session; map load and image were proven. `W04_WolfPresentationV9_Review` image run exited **0**.

**NO GitHub map packaging configuration change:** maps referenced are untracked locally; a GitHub map list pointing to missing sources would create brittle CI and broken releases. A separate asset provenance/import/LFS registration is required before checked-in packaging maps can be adopted.

## 3. Real actor inventory and camera root cause

Real editor **read-only** `EditorLoadingAndSavingUtils.load_map` and `EditorActorSubsystem.get_all_level_actors`:

| Map | Actor count | Primary verified facts |
| --- | ---: | --- |
| `W04_Prototype` | **11** | `DEV_SmokeFloor`, one `PlayerStart`, AshGate, Wolf, Bone Beast, simple lights, runtime smoke |
| `W04_AshenForest_Blockout` | **22** | Six `StaticMeshActor` zone blockouts using engine basic shapes; no final environmental art confirmed |
| `W04_WolfPresentationV9_Review` | **12** | Wolf SkeletalMeshActor, ground test floor, PlayerStart and dev lighting |

The Wolf review map placed its `CelestialWolf` Actor at **(0, 6000, 92.15) cm** but `PlayerStart` at **(-400, 0, 100) cm**. The initial screenshot therefore showed only a gray floor/black sky. A packaged console `BugItGo 0 5400 200 -10 90 0` followed by `HighResShot 1920x1080` showed the actual wolf model and ground shadow; **camera view moved, model/lighting/materials did NOT improve**. Both passes used 1920×1080 real D3D12 and identical packaged map, but different camera poses.

Files all on AsusRog:
- Empty default camera: `after_w04_wolfpresentationv9_review.png` SHA256 `f21aa53d23d7f73a06756bac72a659b40d10a2903912f7737cad37a6a0f53cf3`
- Wolf visible, changed camera: `wolf_camera_probe.png` SHA256 `0afe65b2ee7875316035be82263738bf1c42cc39cef38a1f64833491b6c6fec2`
- Side-by-side comparison `wolf_camera_before_after.png` SHA256 `34b7f2f17619b6d2aa5d5ef2374aac19a6cf5c2ddbf4b69da4ae9b0cc5807ab4`
- Enhanced **camera difference only** `wolf_camera_diff.png` SHA256 `915fe471be1ef3050fb45bb55b6f57c325a84dcd93f1a299021b830c827aba22`
- Actor metadata `editor_map_actor_inventory.json` SHA256 `48CAB2F607ECA63C3AE13E2F12795C676BEE7E8965C57898A26DF41C399E7CE8`.

This comparison is **NOT** the required same-Seed/same-camera before/after art change diff. No genuine FPS delta measured.

## 4. Wolf Animation Blueprint missing native parent: RED → GREEN

**RED actual UE5.7 Editor:** `ABP_CelestialWolf.uasset` loaded as `AnimBlueprint` but generated class `ABP_CelestialWolf_C` failed due to missing native parent `/Script/NARIS_W04.NarisWolfAnimInstance`; these are actual `LogLinker` messages. This source class did not exist under locally checked `NARIS_W04\Source\NARIS_W04\{Public,Private}`. The `ABP` points at actual **WolfUnitsV8 Skeleton**, which is shared by the Wolf V9 presentation mesh.

**Diagnostic class-only fix:** an isolated temporary `UNarisWolfAnimInstance : UAnimInstance` header passed real Editor build, resolving native/Blueprint generated class identity but revealed two real `LogBlueprint` warnings: `Get SmoothedSpeed` missing variable; `Blendspace Player 'BS_Wolf_Locomotion'` invalid `SmoothedSpeed` field. This ruled out merely inventing an empty parent.

**Actual isolated source fix:** `Public/NarisWolfAnimInstance.h` declares reflected, BlueprintReadOnly `float SmoothedSpeed=0.f` and nonnegative editable `float SpeedInterpolationRate=8.f`; `Private/NarisWolfAnimInstance.cpp` overrides `NativeInitializeAnimation` and `NativeUpdateAnimation`, acquires actual `TryGetPawnOwner` velocity in XY via `Size2D()`, interpolates by `FMath::FInterpTo` with nonnegative DeltaSeconds; falls back to speed 0 without an owner. No fabricated animation sequence/IK Retargeter or unlicensed motion assets created. The class does **not** itself certify gameplay animation.

**Real GREEN:** `Build.bat NARIS_W04Editor Win64 Development -NoUBA -MaxParallelActions=2` compiled native class + linked editor DLL **exit 0**, log `wolf_abp_smoothedspeed_build.log` SHA256 `BC35545F3DB5725AF9962ACBB4EA7CE3E9E006347AA0C4FF351CD8AC958F85E2`. Then actual editor Python commandlet `wolf_abp_after_compat.py` loaded **both** `/Script/NARIS_W04.NarisWolfAnimInstance` and `ABP_CelestialWolf_C`, and log `wolf_abp_speed_after.log` reported **0 errors, one unrelated missing localization `.locmeta` warning**, with **no missing-parent / SmoothedSpeed / BlendSpace invalid-field warnings**. Post-fix log SHA256 `29D004F422A336FA9C1A5564CA19AB4072E068A0BEAD8100F24054E1CE100C8E`; preserved prior class-only log `wolf_abp_identity_only.log` SHA256 `C8237920187170D84BC421B625BD595F04599B2AEB984F04A056898336F92F08`.

**TDD proof:** GitHub RED commit `0e8e0180`, [failing run 44856778847](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44856778847) because native parent files absent. GitHub new header `e47fbae25d2701ec794e37e3f3bcd4f08c9c7d12`; new cpp `7f0c71e6d42570b0b60a0e3d9ad8b3198323935c`. [GREEN 44856973290](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44856973290): **77 source tests discovered, 75 passed, 2 GLB tests skipped**, and [NARIS Unreal Validate 44856973168](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44856973168) passed.

Actual post-fix `Project.Maps.PIE` performed against local isolated editor with same `-unattended -nop4 -nullrhi -ExecCmds="Automation RunTests Project.; Quit"`: **Success with 13 warnings, 0 errors, commandlet exit 0**, `wolf_anim_pie.log` SHA256 `BCED5222F664ABECB2DE8D5DE3697423AA740DF02CAD91A0F08AA5FC7541077B`; `wolf_anim_pie_reports/index.json` SHA256 `9773C6521BD92C33934F2A1448BC704FE8A17E55BDB4B47DEC98C25C775471EB`.

**Important scope caveat:** this native code has been committed to the *draft GitHub branch*, but the Wolf V9 `.uasset`, maps and animation binaries are currently local untracked assets, not part of GitHub code package; therefore GitHub CI **does not** prove an end-to-end installed Wolf V9 experience.

## 5. Outstanding quality gates

- Target production advanced hero skeleton (87 runtime bones / 92 authoring entities) absent or unverified; local AshenVessel is 53 bones, CHAR-001 review FBX only 18.
- Ten manifest-specific required AnimMontages were **0/10 loadable** by exact W04 expected paths in the tested local checkout. Four real Wolf V9 Montages exist at different paths but are not substitutes for required production roles.
- No actual proof of Wolf Idle↔Walk↔Run state transitions, foot IK, hit-window/gameplay authority, attack impact class details, server+two-client **combat** replication. Previous local 2-client handshake proves only welcome/join.
- The 13 warnings from Project.Maps.PIE (6 missing UI icons, `/Script/AugmentedReality` and similar) and localization missing `.locmeta` remain.
- The reviewed "AshenForest" map is a coarse **blockout** using engine basic shapes. Screenshot dark horizon is not final AAA environment; do not style it away without actual asset imports, lighting work and matching fixed-view before/after.
- 1920×1080 numerical FPS/frametime/RAM/VRAM **NOT VERIFIED**; do not confuse -benchmark success or a screenshot with a performance pass.

## 6. Safe follow-on and rollback

- Preserve original user checkout and untracked art. For the nine-map trial, rollback only the isolated `DefaultGame.ini` to `DefaultGame_before_mapcook.ini`; retain raw evidence and SHA256.
- Native wolf class rollback in draft branch: revert commits `7f0c71e`, `e47fbae` and their `tests/anim024/test_wolf_anim_native_contract.py` counterpart, then rebuild *isolated* binary and verify expected RED warnings. Do NOT edit or replace `ABP_CelestialWolf.uasset` blindly.
- Review native variable graph bindings in live AnimBP; test actual movement state changes using a stable seeded world, 1920×1080 before/after shot with SAME camera and performance CSV; test combat server + 2 clients; then only consider merging after all mandatory quality gates.
- The new existing local map list is **NOT** checked into GitHub because required `.umap` binary assets are not yet under Git/LFS. Asset-source provenance, LFS import, stable map ownership and PI(E)/Cook regression testing are prerequisites to changing repository packaging settings.

**Reference:** [UE BuildCookRun](https://dev.epicgames.com/documentation/en-us/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine); [Animation Blueprints](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-blueprints-in-unreal-engine); [Screenshot tools](https://dev.epicgames.com/documentation/en-us/unreal-engine/taking-screenshots-in-unreal-engine).
