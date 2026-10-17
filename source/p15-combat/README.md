# NARIS P15 — control and locomotion source revision

This repository directory contains the P15 control/combat plugin, source contracts, scripts and verification reports, targeting Unreal Engine 5.7. It is not a compiled game, an installed project, or a playable EXE. The source-inclusive delivery ZIP separately retains the original and repaired assets; `Originals/`, `SourceAssets/` and `CorrectedUSD/` are not stored in this checkout. No Unreal Editor/UBT runtime was available for this revision.

## Implemented source changes

### 2026-10-18 input lifetime correction

Held movement values must now be refreshed every frame. `InputTimeoutSeconds` defaults to 0.12 real seconds (valid range 0.05–0.5); an expired sample clears the filter and requires new input. A monotonic platform timestamp keeps this deadline independent of gameplay pause/time dilation. The native component rejects paused/ignored/nonlocal input, resets on paused ticks, binds samples to the current Controller and respects ignored look input before driving lock yaw. Controller changes reset filter history. This does not stop existing physical momentum; CharacterMovement still owns braking.

The shared filter also clears released/dead-zone input when frame delta is zero or invalid. `Reports/stale_input_regression_before.txt` records the failing real-header case before repair. Fresh evidence: 195 portable/mocked tests, including 104 compiled shared C++ cases. Native integration remains uncompiled/unplayed here.

Keep explicit Completed/Canceled, pause/UI/focus/possession resets. The timeout bounds missing refresh; it does not detect every viewport-focus change or replace event wiring. Paused-tick and Controller behavior require engine acceptance. The combat buffer still requires explicit `ClearBufferedInput` at UI/pause boundaries. Bindings that set a held movement value only once must migrate to per-frame refresh; otherwise the value expires intentionally.

- An explicitly attached `NarisP15MovementInputComponent` now owns ground movement input and a baseline CharacterMovement profile: speed 400 cm/s, acceleration 1600 cm/s², braking deceleration 1000 cm/s², ground friction 5, separate braking friction 2 and yaw rate 450 degrees/s. Fresh components enable the profile; existing Blueprint instances may retain previously serialized overrides.
- The radial input filter defaults to a 25 ms response constant, with immediate release/reset and the existing diagonal cap. It is a time constant, not a measured device-to-display latency.
- Free movement uses CharacterMovement's orient-to-movement rotation. Combat uses controller-desired rotation. A validated lock target drives a bounded, acceleration-limited desired controller heading. CharacterMovement remains the actor-rotation owner; the component never calls SetActorRotation. Skip ordinary look-yaw input while locked on.
- Voluntary cancel is server validated and requires a positive `NARIS P15 Cancel Window` notify interval on the active montage. It stops the current presentation and defense/hits, clears queued input and preserves stamina spent and the original recovery deadline. It does **not** allow an immediate replacement action before that deadline.
- Applied damage starts a configurable 0.2 s hit recovery and interrupts active action effects/presentation. The old action's later recovery deadline is retained. Set HitRecoverySeconds to 0 only to intentionally disable this new hit-lock policy.
- A replicated control phase distinguishes unavailable setup, free control, active action, cancelled recovery, hit and death. Failed montage playback still spends nothing. A hit arriving during playback acceptance prevents the pending action from committing.
- An existing SpringArm receives free-camera lag speeds 6/8 and combat speeds 18/20, with camera-lag substepping. Higher LagSpeed means less delay. Multiple booms require an explicit component name; the component does not create/reattach a camera or change collision.
- `NarisP15LocomotionAnimInstance` exposes actor-local speed/direction, start/stop/pivot signals, a bounded lean, falling, control phase and turn-in-place intent to an authored Animation Blueprint.
- The buffer now accepts an action at the exact expiry boundary; stale input after a hitch is still discarded.

## Animation and runtime boundary

No Animation Blueprint asset, Blend Space, Start/Stop/Pivot/Turn clips, Foot IK graph, foot-lock curves or new bones were authored. The supplied repaired prototype still has its original 18-joint/idle-only content. The new AnimInstance is a data provider: it cannot animate absent clips or prove planted feet.

Motion Warping aligns root motion to a target; it is not a replacement for Foot IK/foot placement. Build a real skeleton-compatible graph and use correctly authored motion data before claiming that foot sliding is solved. All source meshes, textures and source/repair files are preserved.

## Install and wire

See `START_HERE_AR.md` for explicit wiring and `Docs/CONTROL_ACCEPTANCE_AR.md` for the in-engine acceptance matrix.

1. Use a backed-up UE 5.7 C++ test project; close the Editor and replace the entire old NarisCombat plugin directory. Preserve W04's separate health/control implementation. Never attach both W04 and P15 health owners to the same actor.
2. Compile the Editor target with UHT/UBT. Add one P15 combat component and one P15 movement-input component to the selected test Character. The actor must replicate for the new control-mode RPCs to work in multiplayer.
3. Bind Enhanced Input Axis2D Triggered to SetMoveInput, Completed/Canceled to ResetMoveInput. Remove competing AddMovementInput calls for these axes. Bind actions to Started, and explicitly clear both movement and combat buffers before pause/UI/focus/possession changes.
4. Choose compatible attack/dodge/parry montages, their Slot and weapon sockets as described by GetSetupIssues(). Add the attack-window notify only over contact frames. Cancel-window notifies are optional: absent windows reject RequestCancelCurrentAction. Do not overlap cancel windows or place them at montage time zero.
5. Use SetCombatMode and SetLockOnTarget; pass null to clear the target. The server rejects self/invalid/out-of-world/out-of-range targets. Control-mode changes and action phase are server authoritative, without client prediction; multiplayer latency is not proven below 100 ms.
6. Reparent a copied Animation Blueprint to NarisP15LocomotionAnimInstance only after reviewing its existing parent/event logic. Feed Speed/DirectionDegrees into a real 2D Blend Space, add authored Start/Stop/Pivot/Turn transitions around it (0.1–0.2 s initial blends), evaluate the combat montage Slot, and add Foot IK/stride handling compatible with the actual skeleton and clips.

## Validation

Run `python Scripts/run_local_tests.py` with Python 3.9+ and a real C++17 GCC/Clang compiler. It compiles the same portable headers consumed by the plugin, and runs editor/import/preflight tests against explicit fake boundaries. Read the fresh counts and flags in `Reports/verification.json`; no Unreal API stubs are used to claim UHT/UBT compilation.

`Reports/control_regression_before.txt` records the initial missing-feature failure; `Reports/control_buffer_boundary_before.txt` reproduces a real expiry-boundary regression. `Reports/control_baseline.json` records the 155-test pre-change baseline. The CPU-bind and original archive reports retain their original scope. `Reports/repository_checks.json` records fresh checks against this repository integration; these are source checks, not Unreal execution.

The existing Windows runner still performs source hashes, project preflight, Editor compilation, fresh import, combat-map configuration checks and Development packaging. It does not install this source into an unknown project, author animation graphs, launch PIE or measure performance. Retain its false runtime/input/Slot verification flags until actual playtests pass.

## Preserved intake and Windows build pipeline

`Data/source_uploads.json` pins the eight supplied inputs; `Data/import_spec.json` pins the five active GLBs and required Unreal output classes. The repaired prototype attaches its previously unreferenced Skin and rebuilds rest-pose inverse binds while preserving mesh, texture, weight and animation content. The original `.usdz`-named file is raw USDC; the delivery preserves it and includes an extension-corrected copy. These repairs do not create combat clips or promote assets into the W04 production registry.

To reconstruct a source-inclusive delivery from the exact pinned uploads, use a new output directory:

```sh
python Scripts/build_asset_intake.py --inputs /path/to/project_sources --output /new/path/NARIS_P15_INTEGRATION
python Scripts/verify_sources.py --assets /new/path/NARIS_P15_INTEGRATION/SourceAssets --spec Data/import_spec.json --report /new/path/source_assets_check.json
```

Use compatible montages with RateScale 1, an evaluated montage Slot and `weapon_base`/`weapon_tip` sockets within MaxWeaponReach. A placed P15 test hero must carry `NarisP15Playable`; add a separate damage-enabled Character target with one P15 health owner, Pawn collision and the configured `NarisDamageable` tag. Walls must block Visibility. Do not attach W04 and P15 health owners to the same actor. Existing plugin-class migrations retain the scoped redirect in `Plugins/NarisCombat/Config/DefaultNarisCombat.ini`; review and resave affected Blueprints in the backed-up test project.

From this source directory, after installing and compiling the exact plugin and authoring the test map:

```powershell
.\Scripts\build_win64.ps1 `
  -Project 'C:\NARIS_TEST\CallOfNaris.uproject' `
  -EngineRoot 'C:\Program Files\Epic Games\UE_5.7' `
  -Map '/Game/Maps/CombatTest' `
  -AssetDir 'C:\NARIS_P15_INTEGRATION\SourceAssets' `
  -ImportSpec "$PWD\Data\import_spec.json"
```

The existing runner rejects missing or mismatched plugin files and hashed assets, then builds the Editor, imports into a fresh destination, checks the selected map and packages Development. It does not change system execution policy. Outputs under `Builds/<run-id>/` include preflight, editor/import/map/package logs, artifact hashes and build_result.json. A valid project game executable and nonempty cooked PAK are required, while runtime/input/Slot and performance gates remain open until actually tested.

## Primary references

- CharacterMovement 5.7: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/CharacterMovementComponent?application_version=5.7
- SpringArm 5.7 (LagSpeed semantics): https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SpringArmComponent?application_version=5.7
- Motion Warping 5.7: https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-warping-in-unreal-engine?application_version=5.7
- Foot Placement 5.7: https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimNode_FootPlacement?application_version=5.7
