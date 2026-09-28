# NARIS Offline Update Pack

Target: Unreal Engine 5.7 / NarisCore
Baseline: Win64_PlayFix

## P0 Runtime
- Direct Play is default. Front-end pause is opt-in with `-NarisFrontEnd`.
- Preserve `-NarisQuestSmoke` automated smoke path.
- Legacy input remains Engine.PlayerInput/InputComponent until Enhanced Input is migrated end-to-end.

## P1 Player/Camera
- Third-person spring arm defaults: 420 cm, -12° pitch, camera lag, collision test.
- Movement remains controller-yaw relative.
- Runtime diagnostics must log possessed pawn, view target, input component and pause state.

## P1 Combat
- Light/heavy attack state, dodge i-frames, block/parry windows, lock-on target validation.
- Damage is server-authoritative-ready even for current standalone build.
- Every attack path requires trace/hit confirmation and duplicate-hit suppression.

## P1 AI/Boss
- Spawn validation, target acquisition, leash, attack cooldown, death cleanup.
- Boss phase thresholds data-driven.

## P1 HUD
- Gameplay HUD must never pause or capture movement.
- Pause/front-end menu owns cursor + GameAndUI input only while explicitly open.
- Health/Stamina/Aether/Quest objective + lock-on marker.

## P1 Persistence
- QuickSave/QuickLoad: player transform, health/resources, quest state, pickups, world flags.
- Version save payload and reject incompatible/corrupt payload safely.

## P0 QA gates
1. Boot to gameplay without launch flags.
2. Pawn possessed + ViewTarget pawn.
3. Not paused; cursor hidden; GameOnly input.
4. WASD/mouse movement accepted.
5. Light attack damages exactly once per swing target.
6. Dodge grants then clears invulnerability.
7. QuickSave -> mutate state -> QuickLoad restores state.
8. 3 enemies + boss + companion + pickups + Q_AshenGate available.
9. No Fatal/Error/Failed-to-load in runtime log.
10. Build/Cook/Pak succeeds with zero cook errors.
