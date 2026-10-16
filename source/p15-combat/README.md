# CALL OF NARIS — P15 combat delivery repair

This repairs **NARIS_P15_DELIVERY_20261016.zip**, the combat-source package. It is unrelated to the P15 animation/root-motion archive. This is source plus local verification, not a compiled Unreal game. Original provenance is in `Reports/source_archive.json`.

## Changes and evidence

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

The 25 C++ behavioral cases compile the **same header consumed by the component**. Python tests exercise the actual importer with a fake Unreal API and the read-only preflight using temporary projects. No Unreal API stubs are used to claim an engine compile. See `Reports/verification.json` and `Reports/local_tests.txt` for the executed results.

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
7. Verify in Editor: attack hit/miss; wall obstruction; one damage application per target per swing; zero hits outside notify; stamina depletion/recovery; dodge startup/window/recovery; single-use parry; death; interrupted montages; server ownership and client HUD. Record actual results. No authored montages, skeleton fixes, boss level or final art are bundled.

## Import and package on Windows

Extract the separate P14 source assets; they are not bundled and their older report is not proof of this import. An optional `NARIS_IMPORT_SPEC` JSON maps **every relative GLB path** to required class names, for example `{"hero.glb":["SkeletalMesh","AnimSequence"]}`. Use actual inspected filenames. A successful import only proves the checked editor objects loaded and saved, not motion quality, rig connectivity, animation count or registry approval. New outputs go to `/Game/NARIS/Imported/P15_<run-id>` for review and are not promoted to production registry bindings automatically.

From the extracted delivery directory, in PowerShell:

```powershell
.\Scripts\build_win64.ps1 `
  -Project 'C:\NARIS_TEST\CallOfNaris.uproject' `
  -EngineRoot 'C:\Program Files\Epic Games\UE_5.7' `
  -Map '/Game/Maps/CombatTest' `
  -AssetDir 'C:\NARIS_P14\SourceAssets'
```

The map must already exist and contain the wired Character/targets. The expected Editor target is `<ProjectName>Editor`. This is a Development test build, not Shipping acceptance. The `.bat` wrapper accepts these same four positional paths; the second argument is now **EngineRoot**, replacing the original RunUAT filename. The runner does not change system execution policy. If local policy blocks a script, use the machine's approved script-signing/run process.

Outputs: `Builds/<run-id>/preflight.json`, `editor-build.log`, `import.log`, `import_result.json`, `package.log`, `package_artifacts.json`, `Archive/`, `build_result.json`. Artifact verification requires the project's own Windows game binary under `Binaries/Win64` and a nonempty cooked PAK; a bootstrap or crash reporter alone cannot pass. A package report always keeps `runtime_tested:false`. Preserve the executable and logs, then launch and record a real encounter/playthrough before closing P15 or moving to P16 acceptance.

## Current boundary

Unreal is absent from the local Linux environment; AsusRog was reported offline on 2026-10-16. UHT/UBT compilation, engine importing, montage/socket collision, PIE networking, Windows EXE generation and frame-time profiling remain unexecuted. The remaining W04 release gates stay open. This repair does not claim the game, P15 production acceptance, P16 AI, P17 world/UI or P18 release is complete.

Epic references: [RPC execution/ownership](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-procedure-calls-in-unreal-engine?application_version=5.7), [Animation Notifies](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.7), [Packaging projects](https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project).
