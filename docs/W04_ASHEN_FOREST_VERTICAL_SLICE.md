# W04 — Ashen Forest Vertical Slice

## Identity

World: `W04`
Name: `Ashen Forest`
Role: First complete vertical-slice world

## Player flow

1. Main Menu / Intro
2. Forest Entrance / Wake Area
3. Movement + light-combat onboarding
4. Waystone checkpoint
5. Broken Shrine / Memory Crystal
6. First Whisper narrative trigger — Corrupted Heart step 1
7. Ruined Bridge traversal
8. Whisper Lake companion reveal space
9. Ash Gate progression — Corrupted Heart step 2
10. Celestial Wolf bond — Corrupted Heart step 3
11. Bone Beast Arena — three-phase boss encounter
12. Bone Beast defeat — Corrupted Heart step 4/completion
13. Demo End

**Current slice authority:** Bone Beast is the final boss/completion gate of the implemented W04 vertical slice. Additional Ash Giant / Mist Guardian concepts are not part of the current Shipping acceptance path unless separately integrated and tested.

## Required encounter states

### Memory Crystal
- Player proximity trigger
- Interaction prompt
- Energy restoration
- Quest progression
- Naris dialogue/cinematic trigger

### Bone Beast
- Arena lock
- Telegraphs
- Attack patterns
- Hit reaction
- Defeat state
- Reward/drop
- Quest progression

### Ash Gate
- Locked before the First Whisper / required quest state.
- Progression through the gate advances Corrupted Heart to step 2.
- The Celestial Wolf bond follows the gate progression condition.
- Cinematic/presentation transition remains optional until authored assets are bound.

### Celestial Wolf
- Spawn/acquisition sequence
- Follow behavior
- Track/guide behavior
- Guardian behavior
- Bond state

### Bone Beast — current major boss
- Encounter auto-start / arena lock.
- Three-phase state machine.
- Telegraphs and data-driven attacks.
- Animation-owned impact timing.
- Damage windows / hit reactions.
- Phase transition.
- Defeat state.
- Corrupted Heart completion.
- Demo completion trigger.

## World asset requirements

Minimum production domains:

- ENV-GEO
- ENV-TILE
- ENV-PROP
- ENV-RUIN
- ENV-LAND
- ENV-MAT
- ENV-VFX
- ENV-LIGHT
- ENV-AUDIO
- ENV-ARENA
- CHR
- WPN
- VFX
- SFX
- UI
- CINE
- QUEST

All assets use the immutable NARIS Asset ID contract.

## QA gates

- Spawn / traversal
- Collision
- Camera
- Combat
- AI
- Quest progression
- Companion state
- Boss state transitions
- Save/load
- Audio/VFX triggers
- Performance
- Regression

## Performance target

Profile the complete slice as one runtime sequence. Track frame time, draw calls, texture memory, shader cost, streaming stalls, Niagara cost, and collision/AI cost. Do not approve based on a single static scene.
