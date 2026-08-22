# NARIS v2.0 — Unreal Implementation Backlog

## Runtime decision
The GitHub project is the production source of truth. The browser Three.js build remains a validation/prototype track; the production runtime is Unreal Engine as documented by the project.

## W04 — Ashen Forest vertical slice

### Player
- Third-person locomotion
- Camera follow/chase
- Sprint
- Dodge with invulnerability window
- Light/heavy attack chain
- Parry window
- Hit reaction / stagger

### Energy
- Naris Flame
- Ash Essence
- Ethereal Essence
- Abyssal Essence
- Radiant Essence
- Resonance calculation and feedback

### World
- Forest Entrance
- Broken Shrine
- Ruined Bridge
- Whisper Lake
- Ash Gate
- Bone Beast Arena

### Progression
Memory Crystal → Naris First Whisper → Bone Beast → Ash Gate → Celestial Wolf → Boss → Demo Complete.

### Companion
Celestial Wolf states: Follow, Guard, Track, Attack, Echo Link.

### Boss
Ash Giant/Mist Guardian architecture must support phase transitions, telegraphs, stagger/poise break, rewards and completion events.

### Production data
All runtime assets must have canonical immutable NARIS Asset IDs and follow docs/ASSET_NAMING.md. Runtime delivery should use optimized engine assets; authoring sources remain upstream.

## Definition of Done
A W04 build is not complete until a fresh playtest can boot, traverse the full loop, fight enemies/boss, acquire the wolf, save, reload, and reach Demo Complete without blocking errors.

## QA gates
- no blocking runtime errors
- controller/keyboard input verified
- quest state survives save/load
- boss phase transition verified
- companion state verified
- objective/HUD readability verified
- performance budget measured on target hardware
