# W04 Presentation Production Pass

This pass defines the runtime hooks that final authored assets plug into.

## Celestial Wolf
- Player command: `CompanionMode`.
- Keyboard: `C`.
- Gamepad: D-Pad Up.
- Cycle: Follow -> Guard -> Attack -> Track -> Echo Link -> Follow.
- HUD exposes the localized current mode.
- Existing presentation cues remain authoritative for mode, bond, attack impact and Echo Link pulse.

## Bone Beast attack presentation
Authoritative phase attack requests:
- Phase 1: `ClawSweep`
- Phase 2: `BoneCharge`
- Phase 3: `AshRupture`

`RequestPhaseAttack()` records the gameplay attack and emits `Boss.Attack.<AttackId>`.

Autonomous runtime:
- Bone Beast ticks only while the encounter is active.
- Player must be inside `AttackRange`.
- `AttackIntervalSeconds` gates repeated requests.
- Current phase selects ClawSweep / BoneCharge / AshRupture.
- Smoke fallback can immediately commit through the normal Unreal damage pipeline.
- Production Blueprint sets `bImmediateSmokeAttackImpact=false`; the authored montage owns timing. Add `NARIS Bone Beast Attack Impact` at the contact frame; it calls `CommitAttackImpact()`, which applies damage through Unreal's damage pipeline so hero Parry/Dodge rules remain authoritative.

## Presentation profile
`UNarisPresentationComponent` is the common runtime bridge for:
- Niagara
- positional audio
- world camera shake

Final assets should be assigned through `DA_W04_Presentation`; gameplay classes emit cue IDs and do not hard-code asset paths.

## Required authored cues
- `Boss.Attack.ClawSweep`
- `Boss.Attack.BoneCharge`
- `Boss.Attack.AshRupture`
- `Boss.AttackImpact`
- `Boss.PhaseTransition`
- `Boss.Death`
- `Wolf.Mode.Follow`
- `Wolf.Mode.Guard`
- `Wolf.Mode.Attack`
- `Wolf.Mode.Track`
- `Wolf.Mode.EchoLink`
- `Wolf.Attack`
- `Wolf.AttackImpact`
- `Wolf.EchoLink.Pulse`

## Runtime evidence still required
Source/CI contracts do not prove asset quality. Close this pass only after the Windows editor loads the final profile, montages, Niagara systems, audio and camera shakes and the encounter is playtested.


## Celestial Wolf attack timing
- Runtime Attack mode selects an active Bone Beast target.
- `RequestAttack()` records the pending target and emits `OnAttackRequested`.
- Production montage places `NARIS Celestial Wolf Attack Impact` at the contact frame.
- The notify calls `CommitAttackImpact()`; only that commit path applies boss damage and emits `Wolf.AttackImpact`.
- Smoke mode may set `bImmediateSmokeAttackImpact=true`, but it still uses the same commit path.
- Final production Blueprint must set the smoke fallback to false once authored montage timing is present.

## Boss arena entry
- `ANarisBossArenaController::EncounterTrigger` begins the encounter when the local player enters the boss arena.
- `EncounterStarted` closes the blocker and emits Arena presentation cues.
- Completion/restored completion reopens the arena.
- The encounter still refuses to start unless the Celestial Wolf prerequisite is satisfied.

## Release-candidate rule
Development smoke may contain explicitly unbound presentation payloads. Shipping RC may not.
`Invoke-NarisWindowsReleaseCandidate.ps1` sets `NARIS_PRESENTATION_STRICT=1` and rejects any unbound VFX, audio or camera payload before Shipping BuildCookRun.
