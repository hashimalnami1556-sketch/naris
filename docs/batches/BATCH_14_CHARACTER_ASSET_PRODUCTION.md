# NARIS REALMS — Batch 14 Character & Asset Production

## Goal
Move from gameplay placeholders to a repeatable Blender production factory for characters, bosses, weapons, VFX sockets and engine-ready metadata.

## First production asset
**Gate Guardian — NARIS-GG-001**

- Realm: Ash Gate
- Role: Boss
- Health: 1800
- Damage: 55
- Speed: 2.6
- Attack range: 3.2m
- Phase thresholds: 70% / 40%
- Flee: false
- Element: Void
- Runtime target: GLB / Babylon.js
- Cinematic target: FBX

## Factory
`tools/blender/NARIS_GATE_GUARDIAN_PRODUCTION_FACTORY_v1.py`

The factory creates modular body, armor, weapon, emissive FX, sockets, collision proxy, LOD target markers and gameplay metadata. It is a production blockout/scaffold; final sculpt, retopology, UVs, PBR texturing, rigging and animation remain authored passes.

## Asset naming
`GG_<SYSTEM>_<PART>`

Examples:
- `GG_Chest`
- `GG_Shoulder_L`
- `GG_Gatebreaker_Blade`
- `Socket_Weapon_R`
- `GG_COLLISION_CAPSULE`

## Required final pipeline
Concept → production sheet → sculpt → retopo → UV → PBR → rig → animation → collision → sockets → VFX → GLB optimization → asset registry → runtime validation.

## Next batch
Produce Ash, Rune, Kor and Celestial Wolf using the same factory conventions, then connect the character registry and combat profiles to the Babylon runtime.
