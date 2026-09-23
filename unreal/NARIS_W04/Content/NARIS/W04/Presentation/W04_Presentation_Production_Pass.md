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
The authored montage owns timing. Add `NARIS Bone Beast Attack Impact` at the contact frame; it calls `CommitAttackImpact()`, which applies damage through Unreal's damage pipeline so hero Parry/Dodge rules remain authoritative.

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
