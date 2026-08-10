# W04 Prototype Boss Arena Map Specification

## Arena identity
- World: W04 — Ashen Forest
- Encounter: Bone Beast
- Arena ID: Arena.BoneBeast
- Quest: Quest.W04.CorruptedHeart

## Spatial composition
1. Arrival corridor — safe approach and boss reveal staging.
2. Central combat floor — primary melee engagement zone.
3. Outer hazard ring — environmental pressure; must not invalidate melee readability.
4. Recovery pockets — two protected-but-limited repositioning spaces.
5. Boss anchor — central navigation reference for phase transitions.
6. Exit gate — locked during encounter; released on EncounterComplete.

## Runtime volumes
- CombatBounds: prevents boss/player drift outside the authored encounter space.
- BossNavigationBounds: constrains boss navigation.
- CameraCombatVolume: establishes cinematic/combat framing.
- IntroCameraVolume: controls arrival and reveal.
- HazardVolumes: broadcast environment damage/events.
- PhaseVolumes: optional authored regions for phase-specific VFX/audio changes.

## Spawn points
- PlayerStart_W04_Boss
- BoneBeastStart
- AddSpawn_A
- AddSpawn_B
- RecoveryPoint_A
- RecoveryPoint_B

## Event contract
EncounterStarted -> intro sequence -> combat active
AttackStart -> animation/VFX/audio consumers
Impact -> hit reaction/VFX/audio consumers
Stagger -> UI/VFX/audio consumers
PhaseTransition -> phase presentation + encounter tuning consumers
Death -> death sequence
EncounterComplete -> quest + gate + reward consumers

## Authority
Gameplay C++ owns encounter state. Level Blueprint/Blueprint Actors consume events and provide presentation/orchestration only.

## Acceptance criteria
- Player cannot leave CombatBounds during active encounter.
- Boss cannot navigate outside BossNavigationBounds.
- Intro camera never persists after combat activation.
- Exit gate cannot open before EncounterComplete.
- Every phase transition emits exactly one authoritative transition event.
- Arena hazards never bypass normal encounter damage rules.
