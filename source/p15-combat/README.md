# CALL OF NARIS — P15 combat delivery repair

This repairs **NARIS_P15_DELIVERY_20261016.zip**, the combat-source package. It is unrelated to the P15 animation/root-motion archive. This is source plus local verification, not a compiled Unreal game. Original provenance is in `Reports/source_archive.json`.

## Changes and evidence

### Montage lifecycle and combat-map gate

The authority now calls `Montage_Play` before spending stamina or activating defense. The same portable rules tested by GCC reserve the presentation step against reentrant requests, reject failed playback without a cost or defense window, and recheck death/state before commitment. Accepted actions are not played a second time on the server by the multicast.

Interrupted/ended montages or an AnimInstance replacement cancel active hits/parry/invulnerability immediately, while preserving spent stamina and the original recovery deadline. Server cancellation stops the matching client montage. Actor teardown removes animation/damage delegates without sending teardown RPCs. These engine hooks are source changes; UHT/UBT and multiplayer execution remain unverified here.

`GetSetupIssues()` exposes native editor diagnostics for a missing mesh/Skeleton/AnimBlueprint, incompatible montage Skeletons, invalid rates/durations/costs, missing sockets, missing Slot tracks or absent/out-of-bounds attack-window notifies. A checked Slot track and assigned AnimBlueprint do **not** prove that the graph evaluates that Slot or that input is wired.

The Windows pipeline now runs `Unreal/validate_combat_map.py` after import and before packaging. In the explicitly selected test map:

- Tag each **placed test Character** that should be inspected `NarisP15Playable`; attach exactly one P15 combat component and complete its native setup diagnostics.
- Add a separate Character target with one P15 health owner, damage enabled and the Actor Tag configured by the hero's `DamageableTag` (default `NarisDamageable`). A hero cannot satisfy its own target requirement. The gate rejects mixed W04/P15 health owners on either side.
- The validator reads the map and actor properties without creating/saving/retagging anything. Missing configuration produces a fresh failed report and prevents packaging. It checks loaded Editor actors; it does not verify streamed/unloaded gameplay content or a GameMode's dynamically spawned pawn.
- `combat_map_report.json` always keeps `runtime_tested:false`, `input_wiring_verified:false` and `anim_blueprint_slot_evaluated:false`. PIE damage, input, visual motion, networking and performance remain required.

### 2026-10-17 actual attached-source intake

The supplied prototype has 18 joints and one idle clip, but its mesh node never references the Skin. Attaching it alone is insufficient: its inverse-bind data also fails the conservative rest-pose gate. `Scripts/build_asset_intake.py` preserves the original and produces `Character1_NARIS_Rigged_Prototype_FIXED.glb`, attaches Skin 0 and rebuilds column-major inverse binds as `inverse(jointWorld) * meshWorld`. Mesh, textures, weights and original animation data are preserved. It does not manufacture attack/dodge/parry clips or improve skin-weight artistry.

`Data/source_uploads.json` pins all eight supplied source files. `Data/import_spec.json` pins the exact five active GLBs, their hashes and required Unreal classes. Raw Character 1/3 are static source meshes; the repaired prototype requires SkeletalMesh, Skeleton and AnimSequence outputs. No source is automatically approved for W04 production. The supplied `.usdz` is a raw `PXR-USDC` layer: an extension-corrected `.usdc` copy is provided separately, with the original retained; no USD semantic validation or USDZ conversion is claimed.

The Python-only gate checks embedded GLB framing, buffers/accessors, finite mesh data, triangle indices, hierarchy, skin attachment, vertex weights and **rest-pose bind preservation**. It deliberately rejects unsupported sparse/external-buffer/nontriangle inputs. It is a limited prototype intake, not the complete Khronos validator; a valid glTF authored with a non-bind rest pose may require a different pipeline. Windows now validates the exact hashed input set before compiling and again before editor import; stale inherited import-spec environment variables are replaced and restored.

To reproduce a source-inclusive delivery from the pinned uploads (no existing output directory is overwritten):

```sh
python Scripts/build_asset_intake.py --inputs /path/to/project_sources --output /new/path/NARIS_P15_INTEGRATION
python Scripts/verify_sources.py --assets /new/path/NARIS_P15_INTEGRATION/SourceAssets --spec Data/import_spec.json --report Reports/source_assets_check.json
```

`Tests/check_real_bind.py` is an additional independent NumPy CPU check for this translation-only uploaded rig; it checks all vertex positions in the rest pose and verifies that non-bind binary bytes and the idle animation remain unchanged. It is distinct from the dependency-free local unit suite and is not Unreal gameplay evidence.

- Shared C++17 rules now reject nonfinite/negative configuration, invalid damage/time and insufficient stamina. An active action prevents repeated attack/dodge/parry requests. Regeneration accounts only for time after its delay.
- Dodge has a startup, invulnerability window and vulnerable recovery. Parry consumes one valid incoming hit. Death blocks actions and hit windows.
- Unreal source adds montage presentation via server-initiated multicast, a native attack-window notify, socket sweeps, obstruction checks and once-per-target damage per attack. Server damage uses `ApplyDamage` / `OnTakeAnyDamage`. These engine paths are **not compiled or playtested here**.
- The reflected class is `UNarisP15CombatComponent`. W04 already owns a different `UNarisCombatComponent`; its gameplay implementation is preserved. This package is isolated under `source/p15-combat`, not automatically enabled in W04.
- Import fails on empty/missing input, stale destinations/results, missing/unloadable/unsaved objects and missing skeletal Skeletons. Each run gets a new Unreal destination. Optional exact file/class requirements prevent omitted files or animations from passing.
- Windows runner performs read-only preflight, Editor compilation, fresh import and Development packaging, checking each step and the resulting game executable. It records logs, hashes and a failed report on errors. It does not launch or performance-test the packaged game.

Run local tests with Python 3.9+ and a C++17 GCC/Clang compiler (the supplied test runner uses GCC-style command-line flags):

```sh
python Scripts/run_local_tests.py
```

The 44 C++ behavioral cases compile the **same header consumed by the component**. Python tests exercise source fixtures, the actual importer and combat-map runner with a fake Unreal API, plus read-only preflight/artifact checks using temporary projects. No Unreal API stubs are used to claim an engine compile. See `Reports/verification.json` and `Reports/local_tests.txt` for the executed results.

## Install without overwriting W04 combat

1. Use a backup/test checkout of a UE 5.7 C++ project. Preserve existing maps, plugin binaries, Blueprint assets and source before changing anything. Compile logs must identify the engine actually used.
2. Copy **only** `Plugins/NarisCombat` into the test project's `Plugins`. If an older NarisCombat plugin is installed, move that whole directory outside the project first; merging directories can leave duplicate reflected classes. This delivery does not automatically install or delete anything.
3. Explicitly enable `NarisCombat`, `PythonScriptPlugin`, `EditorScriptingUtilities` and the engine's glTF/Interchange importer in the `.uproject`/Editor. Add `NarisCombat` as a dependency if the project's own C++ includes this plugin's headers. The build preflight refuses missing, disabled or mismatched plugin files.
4. Compile the Editor target and reopen the project. Add **NarisP15CombatComponent** to a test Character. Use this component as that character's single health/defense owner; attaching both it and W04's combat component would create separate health states. No W04 production actor is converted automatically.
5. For existing Blueprints based on the old plugin class, preserve their packages, then verify the redirect in `Config/DefaultNarisCombat.ini`. Copy that `[CoreRedirects]` entry into the project's `Config/DefaultEngine.ini` when packaging/migrating, resave affected Blueprints and check all bindings. It redirects only `/Script/NarisCombat.NarisCombatComponent`, never `/Script/NARIS_W04.NarisCombatComponent`.

## Wire a real test encounter

1. Assign compatible LightAttack, Dodge and Parry **AnimMontages** on the component defaults. Their `RateScale` must be 1; action lock duration uses the montage length. Missing montages reject the corresponding request without consuming stamina. Animation Blueprints must evaluate the montage Slot. The character skeletal mesh must have an AnimInstance.
2. Add `weapon_base` and `weapon_tip` sockets to the Character's skeletal mesh/skeleton along the blade, or set the socket properties to existing names. Both sockets must stay inside `MaxWeaponReach`. This prototype reads Character mesh sockets, not a separate weapon actor.
3. Add the **NARIS P15 Attack Window** notify state to the light-attack montage only during contact frames. A closed window applies no hits; reopening it in the same attack cannot hit the same actor twice. Add the `NarisDamageable` Actor Tag to test targets, use Pawn collision, and block Visibility on walls.
4. Bind Enhanced Input started events to `RequestLightAttack`, `RequestDodge`, `RequestParry`. Drive HUD through `OnVitalsChanged`; `OnActionPresented` is cosmetic and must not apply damage. Incoming test damage should call `ApplyDamage` once; the component receives it through `OnTakeAnyDamage`.
5. For dodge travel, supply an appropriate root-motion montage and configure Character/AnimBlueprint root-motion handling. This package supplies timed defense, not fabricated animation data or a new movement controller.
6. For networking, enable replication on the Character and ensure the requesting client owns it. Requests are checked on authority, and accepted presentation is multicasted. There is no client prediction, rollback, GAS, replicated boss AI or late-join montage recovery. Validate standalone and two-client PIE separately.
7. Verify in Editor: attack hit/miss; wall obstruction; one damage application per target per swing; zero hits outside notify; stamina depletion/recovery; dodge startup/window/recovery; single-use parry; death; interrupted montages; server ownership and client HUD. Record actual results. No authored combat montages, boss level or approved final art are bundled.

## Import and package on Windows

Use the source-inclusive delivery's `SourceAssets` and version 2 `Data/import_spec.json`, or supply your own inspected and hashed version 2 contract. The build runner requires it. The standalone Editor importer also accepts the legacy class-only `NARIS_IMPORT_SPEC` mapping for compatibility; that weaker form does not pin content hashes. A successful import only proves the checked editor objects loaded and saved, not visual motion quality, animation counts, material quality or registry approval. New outputs go to `/Game/NARIS/Imported/P15_<run-id>` for review and are not promoted to production registry bindings automatically.

From the extracted delivery directory, in PowerShell:

```powershell
.\Scripts\build_win64.ps1 `
  -Project 'C:\NARIS_TEST\CallOfNaris.uproject' `
  -EngineRoot 'C:\Program Files\Epic Games\UE_5.7' `
  -Map '/Game/Maps/CombatTest' `
  -AssetDir 'C:\NARIS_P15_INTEGRATION\SourceAssets' `
  -ImportSpec 'C:\NARIS_P15_INTEGRATION\Data\import_spec.json'
```

The map must already exist and contain the wired Character/targets. The expected Editor target is `<ProjectName>Editor`. This is a Development test build, not Shipping acceptance. The `.bat` wrapper accepts the four positional paths plus an optional fifth import-spec path; without it the contract must exist at `<AssetDir>/../Data/import_spec.json`. The second argument is **EngineRoot**, replacing the original RunUAT filename. The runner does not change system execution policy. If local policy blocks a script, use the machine's approved script-signing/run process.

Outputs: `Builds/<run-id>/preflight.json`, `editor-build.log`, `import.log`, `import_result.json`, `package.log`, `package_artifacts.json`, `Archive/`, `build_result.json`. Artifact verification requires the project's own Windows game binary under `Binaries/Win64` and a nonempty cooked PAK; a bootstrap or crash reporter alone cannot pass. A package report always keeps `runtime_tested:false`. Preserve the executable and logs, then launch and record a real encounter/playthrough before closing P15 or moving to P16 acceptance.

## Current boundary

Unreal is absent from the local Linux environment; AsusRog was reported offline again on 2026-10-17. UHT/UBT compilation, engine importing, montage/socket collision, PIE networking, Windows EXE generation and frame-time profiling remain unexecuted. The remaining W04 release gates stay open. This repair does not claim the game, P15 production acceptance, P16 AI, P17 world/UI or P18 release is complete.

Epic references: [RPC execution/ownership](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine?application_version=5.7), [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.7), [Packaging projects](https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project).


## Input responsiveness continuation — 2026-10-17

The optional P15 plugin now offers a **150 ms, one-entry combat input buffer**. Requests received only within the last buffer interval of recovery can be queued. The latest different valid request replaces the pending one; repeating the same request does not extend its expiry. Buffering spends no stamina and grants no defense. The server consumes the pending request once when recovery ends, through the existing accepted-playback path. Failed playback is not retried automatically. Death, interrupted playback, AnimInstance replacement and teardown clear pending input. Normal montage completion preserves the queued request until recovery/expiry. A frame hitch beyond expiry drops it. Set `InputBufferSeconds=0` to disable; supported range is 0–0.3 seconds. There are no early cancel windows or client prediction in this change.

### Opt-in ground movement input

`UNarisP15MovementInputComponent` shapes 2D input, without directly modifying velocity, physics or replication. It is **not attached automatically** and does not alter W04's existing axis bindings. Use a backed-up standalone P15 test Character; do not add a second movement producer to W04.

1. Add the component to the test Character. Feed `SetMoveInput` with X=right, Y=forward from your existing input binding. For Enhanced Input, use an Axis2D action's `Triggered` value; connect both `Completed` and `Canceled` to `ResetMoveInput`. Bind combat requests to a single press/`Started`, not a continuously firing `Triggered` action.
2. Remove direct `AddMovementInput` calls for those same axes. Use exactly one source. The component applies camera-yaw-relative input only to the locally controlled, unblocked, grounded Character. Air/swim/AI movement is outside this component's scope.
3. Call combat `ClearBufferedInput` before pausing/changing input mode (it forwards to the owning server). Reset movement input explicitly on pause, focus loss, UI input-mode changes and unpossession; callbacks may stop arriving when a mapping is removed. Held raw input is otherwise retained until the binding sends zero/reset. Do not rely solely on a paused Tick to clear input.
4. Initial filter values: radial dead zone 0.12, exponent 1.4, response time constant 0.04 s. Disable equivalent Enhanced Input modifiers to avoid applying the curve/dead zone twice; alternatively set this component's dead zone to 0 and exponent to 1. The exponential filter is frame-independent for constant input; release clears input immediately so CharacterMovement owns braking. Diagonal magnitude is capped at 1.
5. `bApplyMovementProfile` defaults to **false**. Enable only in the test Character to try yaw 450 deg/s, acceleration 1600 cm/s², walking braking deceleration 1400 cm/s² and separate braking friction 2. Existing walk/sprint speed, ground friction, capsule, camera and asset settings are preserved. These are exploratory values, not accepted production tuning. Existing `BrakingFrictionFactor` still multiplies braking friction. Higher deceleration generally stops faster; too little can extend sliding.
6. Build UHT/UBT before claiming integration. Test keyboard and controller at 30/60/120 FPS, starts/stops/180-degree reversals, slow stick movement, diagonal movement, pause/focus recovery, root-motion montage interruption, and one queued action at recovery. Record response time, stopping distance, foot slip, Slot evaluation and client/server behavior separately.

### Unclosed presentation work

No Blend Space, Start/Stop/Pivot clips, Foot IK/Control Rig, motion/stride/orientation warping graph, upper-body layer or new combat animation was authored here. The supplied repaired rig still contains one idle animation. These require compatible authored content, skeleton/bone/curve inspection and actual Unreal visual acceptance. The canonical W04 controller continues using its existing legacy bindings; no Enhanced Input asset migration is claimed.

Evidence: 155 portable/mocked tests pass, including 64 compiled C++ cases exercising shared combat/filter headers. The new reflected component, montage callbacks and CharacterMovement profile have not been compiled or executed in Unreal. No EXE or measured gameplay improvement is claimed.

Official references: [CharacterMovementComponent](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/UCharacterMovementComponent), [Enhanced Input](https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine).
