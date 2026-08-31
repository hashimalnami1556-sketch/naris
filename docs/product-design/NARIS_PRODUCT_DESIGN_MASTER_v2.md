# NARIS — Product Design Master v2

Status: Production Design Baseline
Owner: NARIS Studios / Alnami Company
Game: CALL OF NARIS

## 1. Product North Star

NARIS is a cinematic dark-fantasy action RPG. The product experience must feel premium, mysterious, readable, and emotionally coherent from title screen through combat, exploration, dialogue, boss encounters, and progression.

Primary pillars:
1. Cinematic exploration
2. Tactical readable combat
3. Memory-driven narrative
4. Strong companion relationship
5. Distinct world identities
6. Consistent visual language across all surfaces

## 2. Canonical Visual System

Palette families:
- Naris Fire — ember/orange
- Aether Violet — supernatural energy
- Mist Cyan — spirit/atmosphere
- Ancient Gold — relic/UI emphasis
- Ash Black — structural darks
- Blood Ember — danger/corruption
- Spirit Green — healing/positive state

Rule: dark fantasy must not become grayscale. Key shots require controlled color contrast and a readable focal hierarchy.

## 3. Character Product System

### Ashen Vessel
- Role: player protagonist
- Age: 27
- Height: 183 cm
- Body: athletic
- Signature: burned cloak, ancient armor, ember veins, runic scars
- Production layers: head, hair, eyes, torso, armor, cape, weapon, FX, shadow

### Celestial Wolf
- Role: guide / tracker / guardian / lore keeper
- Signature: astral body, cyan-violet aura, mist trail, stellar particles
- Abilities: Spirit Dash, Echo Link, Astral Mark, Soul Vision, Celestial Roar

### Core enemy/boss set
Bone Beast, Ash Giant, Mist Guardian, Veil Mother, Fallen Warden.

## 4. World Product System

Initial vertical-slice environment: Ashen Forest.

Required landmarks:
- Forest Entrance
- Broken Shrine
- Ruined Bridge
- Whisper Lake
- Ash Gate
- Bone Beast Arena

Environment asset classes:
- modular terrain
- cliffs/rocks
- trees/roots
- ruins
- gates/shrines
- props
- decals
- foliage
- fog volumes
- VFX anchors
- lighting probes

## 5. UX Architecture

Core flow:
Boot → Main Menu → New Game → Intro Cinematic → Exploration → Tutorial Combat → Naris Whisper → Memory Crystal → Bone Beast → Ash Gate → Companion Reveal → Slice Finale.

HUD must prioritize:
1. health/stamina or combat resources
2. immediate threat feedback
3. objective guidance
4. companion state
5. contextual interaction

Secondary surfaces:
Inventory, Map, Journal/Lore, Skills, Settings, Pause, Save/Load.

## 6. Interaction Principles

- Every interactive object has a clear affordance.
- Combat telegraphs must be readable without breaking immersion.
- Important narrative moments may override HUD density.
- UI should use world-compatible framing, not generic mobile/game templates.
- Accessibility settings must not alter canonical art direction.

## 7. 3D Asset Acceptance Standard

Every final 3D asset must include:
- immutable NARIS Asset ID
- source file
- GLB/glTF interchange export
- engine import target
- PBR materials
- collision definition where required
- LOD strategy
- naming-compliant textures
- preview renders
- QA status

Preferred asset naming pattern:
NARIS_[DOMAIN]_[ASSET]_[VARIANT]_[LOD/TYPE]

## 8. Production Gate

No asset is considered final because a model exists. Final acceptance requires visual match, topology/scale sanity, material correctness, runtime performance suitability, naming, registry entry, and QA evidence.

## 9. Tool Handoffs

Mesh generation: prepare model-ready briefs and validation criteria.
Design: prepare component/layout specifications and interaction states.
Game Studio: integrate accepted assets into the playable vertical slice.
Slack: distribute status/handoff summaries when a connected workspace is available.

## 10. Definition of Done — Vertical Slice

A player can launch, start a new game, move, fight, collect an item, trigger dialogue, receive a quest, open the Ash Gate, encounter the Celestial Wolf, fight a major enemy/boss, save/load, and reach the slice-ending state without a blocker.
