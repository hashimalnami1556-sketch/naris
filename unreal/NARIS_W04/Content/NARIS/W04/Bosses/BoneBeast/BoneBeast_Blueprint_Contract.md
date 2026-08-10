# Bone Beast Blueprint Contract

## Components
- BoneBeastBoss (native gameplay actor)
- BoneBeastCombatComponent
- BoneBeastPhaseComponent
- Capsule/mesh collision
- Optional arena interaction component

## Blueprint responsibilities
- Assign skeletal mesh and animation assets.
- Assign `DA_BoneBeast`.
- Bind `OnBossEvent` to presentation handlers.
- Route AttackStart/Impact/Stagger/PhaseTransition/Death to Animation, Niagara and Audio.
- Never mutate authoritative health/phase directly.

## Required events
- Event_Boss_EncounterStarted
- Event_Boss_AttackStart
- Event_Boss_Impact
- Event_Boss_Stagger
- Event_Boss_PhaseTransition
- Event_Boss_Death
- Event_Boss_EncounterComplete

## Required references
- Arena: `Arena.BoneBeast`
- World: `World.W04.AshenForest`
- Quest: `Quest.W04.CorruptedHeart`
