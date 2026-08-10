# W04 Event Pipeline

```text
BossController
  -> Gameplay Tag / Boss Event
      -> Animation Notify
      -> Niagara / VFX
      -> Audio Cue
      -> UI Boss Bar
      -> Quest State
```

## Authoritative events
- AttackStart
- Impact
- ParryWindow
- PhaseTransition
- Death
- EncounterComplete

## Integration rule
One authoritative gameplay event may fan out to presentation systems. Presentation systems must not independently mutate Boss phase/state.
