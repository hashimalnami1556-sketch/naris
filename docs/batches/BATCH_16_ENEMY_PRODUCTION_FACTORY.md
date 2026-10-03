# BATCH 16 — NARIS Enemy Production Factory

## Objective
Move the four core hostile archetypes from design-only definitions into a deterministic asset-production contract and Babylon runtime factory.

## Assets
| Key | Asset ID | Realm | HP | Damage | Speed | Range |
|---|---|---|---:|---:|---:|---:|
| Ashen Shade | NARIS-W04-ENM-ASHEN-SHADE-0001 | Ashen Forest | 220 | 24 | 3.8 | 2.8m |
| Thorn Creature | NARIS-W07-ENM-THORN-CREATURE-0001 | Bell Swamp | 300 | 32 | 4.6 | 2.2m |
| Stone Guardian | NARIS-W08-ENM-STONE-GUARDIAN-0001 | Twilight Castle | 650 | 55 | 1.7 | 3.2m |
| Gate Guardian | NARIS-GG-001 | Ash Gate | 1800 | 55 | 2.6 | 3.2m |

## Production scaffold
`tools/blender/NARIS_ENEMY_PRODUCTION_FACTORY_v1.py` creates modular bodies, attack silhouettes, emissive cores, collision-ready roots, sockets and gameplay metadata. It intentionally remains a scaffold until final sculpt, retopology, UV, PBR, rigging and animation passes are supplied.

## Runtime
`apps/naris-browser-runtime/src/game/enemies/EnemyFactory.ts` establishes typed profiles and runtime spawn/damage contracts. `EnemyAI.ts` implements Sense → Decision → Action state flow. `BossController.ts` now supports phase 1/2/3 and execution thresholds at 70% / 40% / 12%, with phase-specific movement, cooldown, damage and attack telegraph timing.

## Required next production passes
1. Replace procedural meshes with approved GLB assets.
2. Add authored attack, stagger, death and locomotion animations.
3. Add real hitboxes/hurtboxes and attack-frame windows.
4. Add NavMesh/raycast avoidance and arena bounds.
5. Connect boss telegraphs to CameraDirector, VFX and audio.
6. Wire defeat → quest progress → gate unlock → save checkpoint.
7. Run TypeScript, unit and browser playtest gates before merge.
