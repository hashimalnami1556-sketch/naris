# Bone Beast Presentation Contract

## Animation
- AM_BoneBeast_Intro
- AM_BoneBeast_Idle
- AM_BoneBeast_Attack_Light
- AM_BoneBeast_Attack_Heavy
- AM_BoneBeast_Stagger
- AM_BoneBeast_PhaseTransition
- AM_BoneBeast_Death

## Animation Notifies
- AN_Boss_AttackStart
- AN_Boss_Impact
- AN_Boss_Recovery
- AN_Boss_Stagger
- AN_Boss_PhaseCue

Gameplay state remains authoritative in `ABoneBeastBoss`. The native `NARIS Bone Beast Attack Impact` notify commits the already-requested attack at the authored contact frame through `CommitAttackImpact()`; it does not select phase, damage, quest state, or encounter completion.

## Niagara
- NS_BoneBeast_Aura
- NS_BoneBeast_AttackImpact
- NS_BoneBeast_Stagger
- NS_BoneBeast_PhaseTransition
- NS_BoneBeast_Death
- NS_W04_AshenForest_Hazard

## Audio
- AC_BoneBeast_Vocal_Idle
- AC_BoneBeast_Attack
- AC_BoneBeast_Impact
- AC_BoneBeast_Stagger
- AC_BoneBeast_PhaseTransition
- AC_BoneBeast_Death
- AM_W04_BoneBeast_Battle

## Event mapping
| Gameplay event | Animation | Niagara | Audio |
|---|---|---|---|
| AttackStart | attack montage | attack charge | attack cue |
| Impact | impact notify | impact burst | impact cue |
| Stagger | stagger montage | stagger burst | stagger cue |
| PhaseTransition | transition montage | transition effect | phase cue |
| Death | death montage | death effect | death cue |


## Phase attack IDs
- Phase 1: ClawSweep
- Phase 2: BoneCharge
- Phase 3: AshRupture

Use `RequestPhaseAttack()` to select the phase attack, then let the authored montage place `NARIS Bone Beast Attack Impact` at contact.
