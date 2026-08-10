# W04 Unreal Engine Class Scaffold

## Purpose
Implementation contract for the W04 Bone Beast vertical slice. This is a source-level scaffold specification, not a claim that compiled Unreal binaries are present in the repository.

## Classes
- `ABoneBeastBossController`
- `UBoneBeastDataAsset`
- `UBoneBeastCombatComponent`
- `UBoneBeastPhaseComponent`
- `UBoneBeastEventSubsystem`

## Responsibilities
### ABoneBeastBossController
Owns encounter state, phase transitions, attack selection and encounter completion.

### UBoneBeastDataAsset
Owns tunable data: phase definitions, attacks, damage profiles, telegraphs, rewards and quest references.

### UBoneBeastCombatComponent
Resolves attacks, hit windows, damage, stamina pressure and stagger interaction.

### UBoneBeastPhaseComponent
Evaluates authoritative phase thresholds and emits phase transition events exactly once.

### UBoneBeastEventSubsystem
Provides the presentation/gameplay event bridge for Animation, Niagara, Audio, UI and Quest consumers.

## Authority rule
Boss state and phase are gameplay-authoritative. Presentation systems consume events and must not independently mutate the encounter state.

## Suggested Unreal assets
- `DA_BoneBeast`
- `ABP_BoneBeast`
- `AM_BoneBeast_*`
- `NS_BoneBeast_*`
- `AC_BoneBeast_*`
- `WBP_BossHealth_BoneBeast`
