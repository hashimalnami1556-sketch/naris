# W04 Gameplay Tags

## Scope
Canonical gameplay tags for the W04 Bone Beast vertical slice.

## Tags
- `Boss.BoneBeast`
- `Boss.Phase.P1`
- `Boss.Phase.P2`
- `Boss.Phase.P3`
- `Boss.State.Idle`
- `Boss.State.Engage`
- `Boss.State.Attack`
- `Boss.State.Defend`
- `Boss.State.Stagger`
- `Boss.State.PhaseTransition`
- `Boss.State.Enraged`
- `Boss.State.Death`
- `Combat.Attack.Light`
- `Combat.Attack.Heavy`
- `Combat.Defense.Parry`
- `Combat.Defense.Dodge`
- `Combat.Hit.Impact`
- `World.W04.AshenForest`
- `Quest.W04.CorruptedHeart`
- `Arena.BoneBeast`

## Rule
Gameplay state is authoritative in the Boss/Combat systems. Animation, VFX, Audio and UI consume events/tags; they do not author boss state.
