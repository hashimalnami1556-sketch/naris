# Bone Beast — AI State Machine

```text
IDLE
  ↓ player detected
ENGAGE
  ↓ attack opportunity
ATTACK ↔ DEFEND
  ↓ valid stagger event
STAGGER
  ↓ recovery
ENGAGE

ENGAGE/COMBAT
  ↓ phase threshold
PHASE_TRANSITION
  ↓ transition complete
ENRAGED / PHASE STATE
  ↓ fatal state
DEATH
```

## State contracts
| State | Responsibility | Exit condition |
|---|---|---|
| IDLE | Observe / breathe | Player detected |
| ENGAGE | Close distance | Attack range / threat |
| ATTACK | Select and execute attack | Recovery |
| DEFEND | Guard / evade | Threat cleared |
| STAGGER | Process stagger | Recovery timer |
| PHASE_TRANSITION | Lock combat state and transition | Transition complete |
| ENRAGED | Execute final high-pressure pattern | Death |
| DEATH | Finish encounter | Encounter complete |

## Event rule
State changes are emitted once. VFX, audio, UI and quest systems must subscribe to the emitted event and must not independently infer phase state.
