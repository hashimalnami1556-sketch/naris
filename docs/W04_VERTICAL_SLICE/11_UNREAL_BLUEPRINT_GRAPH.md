# W04 Blueprint Graph Contract

```text
BP_BoneBeast
  ├─ BossController
  ├─ CombatComponent
  ├─ PhaseComponent
  └─ Event Interface

PhaseComponent
  ├─ EvaluateThreshold
  └─ Emit PhaseTransition

CombatComponent
  ├─ SelectAttack
  ├─ AttackStart
  ├─ Impact
  └─ Stagger

Event Bridge
  ├─ Animation
  ├─ Niagara
  ├─ Audio
  ├─ Boss UI
  └─ Quest
```

## Critical implementation rule
Use one authoritative event path. Do not create parallel phase logic in Blueprint, Animation Blueprint, UI or Niagara.

## Save/Reload
Encounter completion must persist through the game's normal save system. Reloading must not resurrect a completed encounter or duplicate quest completion.
