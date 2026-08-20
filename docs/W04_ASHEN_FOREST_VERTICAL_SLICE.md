# W04 — Ashen Forest Vertical Slice

## Identity

World: `W04`
Name: `Ashen Forest`
Role: First complete vertical-slice world

## Player flow

1. Forest Entrance
2. Wake Area
3. Movement tutorial
4. Combat tutorial
5. Memory Crystal
6. Naris first whisper
7. Bone Beast encounter
8. Ash Gate
9. Celestial Wolf acquisition
10. Ash Giant / Mist Guardian encounter
11. Demo End

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
- Locked state before Bone Beast
- Unlock condition after required quest state
- Cinematic transition

### Celestial Wolf
- Spawn/acquisition sequence
- Follow behavior
- Track/guide behavior
- Guardian behavior
- Bond state

### Major boss
- Intro cinematic
- Phase state machine
- Telegraphs
- Damage windows
- Phase transition
- Defeat state
- Demo completion trigger

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
