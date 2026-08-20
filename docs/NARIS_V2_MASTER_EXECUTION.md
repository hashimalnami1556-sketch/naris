# CALL OF NARIS — v2.0 Unified Master Execution

## Purpose

Unify the existing NARIS production architecture into one executable production track. This document is the execution contract for the vertical slice and the bridge to the ten-world production roadmap.

## Runtime decision

The canonical project repository specifies **Unreal Engine** as the runtime owner. The browser/Three.js prototype is treated as a validation/prototyping surface only and must not replace the Unreal production runtime.

## Vertical Slice

`MAIN MENU → INTRO → ASHEN FOREST / WAKE AREA → MOVEMENT → COMBAT → MEMORY CRYSTAL → NARIS WHISPER → BONE BEAST → ASH GATE → CELESTIAL WOLF → ASH GIANT / MIST GUARDIAN → DEMO END`

## Systems to integrate

1. Player controller
2. Third-person camera
3. Movement
4. Attack
5. Dodge
6. Parry
7. Energy
8. Naris Resonance
9. Abilities
10. Interaction
11. Dialogue
12. Quest state machine
13. Inventory
14. Crafting
15. Weapon upgrades
16. Celestial Wolf companion
17. Enemy AI
18. Boss phases
19. World events
20. Map / traversal
21. Save / Load
22. Pause
23. HUD
24. Audio architecture
25. Niagara VFX architecture
26. Cinematic sequencing
27. Localization
28. Accessibility
29. Debug / profiling
30. Playtest telemetry

## Ashen Forest production scope

World ID: **W04**

Required locations:

- Forest Entrance
- Wake Area
- Broken Shrine
- Ruined Bridge
- Whisper Lake
- Ash Gate
- Bone Beast Arena

## Asset traceability

Every asset must follow the repository contract:

`Concept → Approved Concept → Blockout → High Poly → Retopo → UV → Texture → Material → Unreal Integration → Optimization → QA → Approved`

Every asset must receive an immutable ID using:

`NARIS-W<world>-<domain>-<type>-<sequence>`

Runtime and source exports retain the same canonical ID.

## Production gates

A vertical-slice feature is not complete merely because it compiles. It must pass:

- Functional test
- Visual review
- Collision / interaction test
- Performance check
- Save/load check where applicable
- Regression check
- QA approval

## Definition of Done — v2.0 Vertical Slice

The player can boot the game, start the Ashen Forest sequence, move and fight, use Energy/Resonance, interact with the Memory Crystal, trigger Naris's first whisper, defeat Bone Beast, open the Ash Gate, acquire the Celestial Wolf, reach the major boss encounter, defeat or complete the boss sequence, and reach the demo end state. Save/load and restart behavior must be deterministic.

## Ten-world continuation

After W04 vertical-slice validation, the same asset and gameplay contracts extend to:

W01 Frozen Peaks
W02 Forge of Flame
W03 Echoes Desert
W04 Ashen Forest
W05 Silent Abyss
W06 Inverted Towers
W07 Lost Souls Swamp
W08 Astral Fortress
W09 Forgotten Canals
W10 Throne of Naris

## Critical rule

Do not multiply isolated prototype versions. Integrate into the canonical production repository, preserve traceability, and promote only validated systems/assets into the next production gate.
