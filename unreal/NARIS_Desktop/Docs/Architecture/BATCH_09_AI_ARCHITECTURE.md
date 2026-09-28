# NARIS Batch 09 — Advanced AI + Encounter Director

## Runtime architecture
AIController -> AI Perception -> Threat Component -> StateTree -> EQS -> Combat Component (Batch 08).
Encounter Director owns pacing/budget and never chooses exact attacks; individual AI does.

## StateTree
Global evaluators: TargetValid, DistanceToTarget, HealthPct, BossPhase, HasLOS, CombatSlotAvailable.
States: Idle > Patrol > Investigate > Chase > Attack > Evade/Stunned > Dead.
Boss adds Enraged and PhaseTransition gates.

## EQS assets to create in Unreal
- EQS_Naris_MeleePosition: reachable points, LOS, 180–450uu range, avoid occupied combat slots.
- EQS_Naris_RangedPosition: 800–1600uu, LOS, cover bonus, flank score.
- EQS_Naris_AmbushPosition: hidden from player, reachable, 600–1400uu.
- EQS_Naris_BossChargeLane: nav-valid forward lane, collision clearance, arena bounds.

## Coordination
Use combat slots around target. Default 3 simultaneous melee attackers; remaining agents circle, flank, use ranged/control abilities, or wait. Threat combines damage, proximity, healing/support and scripted boss aggro.

## Bone Beast
Phase 1: Roar > stalk > swipe/tail.
Phase 2: unlock Charge and arena reposition.
Phase 3: aggression boost, shorter recovery, support spawn permitted by Encounter Director.
All phase transitions remain owned by Batch 08 BossPhaseComponent.

## Performance
AI perception update intervals scale by distance. Disable expensive EQS while offscreen/dormant. Use significance tiers and Mass/EQS only where population justifies it. Keep gameplay decisions server-authoritative for future multiplayer compatibility.
