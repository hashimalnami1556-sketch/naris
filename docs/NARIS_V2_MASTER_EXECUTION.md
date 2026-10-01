# CALL OF NARIS — v2.1 Unified Master Execution

## Purpose
Unify NARIS production into one evidence-bound execution track for the W04 Ashen Forest vertical slice. The repository remains the single source of truth.

## Runtime decision
**Unreal Engine 5** owns the canonical runtime. Blender is the production DCC. Browser/Babylon/Three.js and Godot packages may be used for prototyping or validation but do not replace the Unreal production runtime.

## Canonical Vertical Slice
`MAIN MENU → AWAKENING → FOREST ENTRANCE → COMBAT TUTORIAL → BROKEN SHRINE / MEMORY CRYSTAL → FIRST WHISPER → ASH GATE → CELESTIAL WOLF → RUINED BRIDGE → BONE BEAST ARENA → BONE BEAST → REWARD → DEMO END`

## W04 locations
- Forest Entrance
- Wake Area
- Broken Shrine
- Whisper Lake vista
- Ash Gate
- Ruined Bridge
- Bone Beast Arena

## Required runtime systems
1. Player controller and third-person camera
2. Locomotion, sprint, dodge and stamina
3. Animation-driven light/heavy combo combat
4. Hitbox/hurtbox, damage, poise, stagger and reactions
5. Parry and lock-on
6. Energy / Naris Resonance / abilities
7. Interaction and dialogue
8. Quest/world-state machine
9. Celestial Wolf companion
10. Enemy AI and Bone Beast phase logic
11. Waystone/checkpoint and deterministic save/load
12. HUD, pause, settings and controller glyphs
13. Audio/MetaSounds and music-state architecture
14. Niagara/VFX and impact feedback
15. Cinematic sequencing
16. Localization/RTL and accessibility
17. Debug, profiling, regression and packaged-build QA

## Asset traceability
Every production asset follows:
`Concept → Approved Concept → Blockout → High Poly → Retopo → UV → Texture → Material → Rig → Animation → Unreal Integration → Optimization → QA → Approved → Release`

Immutable ID format:
`NARIS-W<world>-<domain>-<type>-<sequence>`

`data/MASTER_ASSET_REGISTRY.json` is authoritative. Do not promote a status without evidence.

## P0 RC blockers — 2026-10-01
- Final Ashen Vessel animation/montage set.
- Production combat hit windows, parry and lock-on acceptance.
- Rigged/animated Celestial Wolf runtime asset.
- Rigged/animated Bone Beast runtime asset and phase presentation.
- W04 collision/NavMesh/traversal validation.
- Runtime audio and Niagara payloads.
- Deterministic W04 save/load.
- Controller production pass.
- Unreal smoke/full-playthrough test.
- Profiling and Win64 packaged-build evidence.

## Production gates
A feature is not complete merely because it compiles. It must pass:
- Functional test
- Visual review
- Collision/interaction test
- Animation/notify validation where applicable
- Audio/VFX binding validation where applicable
- Performance check
- Save/load check where applicable
- Regression check
- QA approval

## Definition of Done — W04 Vertical Slice
The player can launch a packaged Win64 build, start the Ashen Forest sequence, complete movement/combat onboarding, interact with the Memory Crystal, trigger First Whisper, open Ash Gate, acquire/use the Celestial Wolf, traverse Ruined Bridge, defeat Bone Beast through validated phases, receive the reward and reach Demo End. Restart/save/load behavior is deterministic and the build meets agreed performance/QA budgets.

## Scope control
Do not expand production into additional worlds, multiplayer, or large catalogs until W04 passes the RC gate.

## Ten-world continuation
After W04 RC validation, reuse the same contracts for W01 Frozen Peaks, W02 Forge of Flame, W03 Echoes Desert, W05 Silent Abyss, W06 Inverted Towers, W07 Lost Souls Swamp, W08 Astral Fortress, W09 Forgotten Canals and W10 Throne of Naris.

## Current audit
See `docs/production/NARIS_VERTICAL_SLICE_AUDIT_2026-10-01.md`.
