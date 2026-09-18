# W04 ACTOR BLUEPRINT CONTRACTS

## BP_NarisHero
Components: Capsule, CharacterMovement, CameraBoom, FollowCamera, NarisCombatComponent, NarisEnergyComponent, Interaction, LockOn.
Inputs: Move, Look, LightAttack, HeavyAttack, Dodge, Parry, EssenceNext, EssencePrevious, ResonanceBurst, Interact.

## BP_CelestialWolf
Modes: Follow, Guard, Attack, Track, EchoLink.
Tags: Companion.CelestialWolf.

## BP_BoneBeast
Components: NarisCombatComponent, BoneBeastCombatComponent, BoneBeastPhaseComponent, AIController, NavMovement.
Phases: P1/P2/P3.
Tags: Boss.BoneBeast, Boss.BoneBeast.Phase.P1/P2/P3.

## Acceptance
Actors must expose health/poise/energy/events to Blueprint and remain data-driven.
