# CALL OF NARIS — MASTER ROADMAP

**Primary target:** Unreal Engine 5.4+ / Windows PC  
**Primary slice:** W04 — Ashen Forest  
**Current integration level:** v1.9 Master Integration  
**Public release:** gated / disabled until QA acceptance

## Integrated foundation

- Canonical asset registry and production IDs.
- Ten-world environment/biome matrix.
- Unreal W04 bootstrap project.
- Gameplay Tags and module dependencies.
- Runtime combat contracts: health, poise, stagger, execution, resonance.
- Five-essence system contracts.
- Quest/inventory/dialogue/interaction contracts.
- Celestial Wolf companion and Echo Link design/runtime contracts.
- Boss phase/cinematic/localization/settings/build contracts.
- Save/load and release-gate architecture.
- Deterministic AssetForge world generator with 99-biome catalog.
- PC-first packaging and playtest validation plan.

## v1.9 — Unified Integration Build

Goal: eliminate disconnected prototype layers and make the repository describe one canonical Unreal production path.

Deliverables:

1. Master integration specification.
2. W04 vertical-slice contract.
3. AssetForge world-data generator.
4. machine-readable integration manifest.
5. Windows PC as first executable target.
6. internal playtest gate retained.

## v2.0 — Playable PC Vertical Slice

Definition of Done:

1. Main Menu
2. Intro cinematic
3. Wake Area
4. movement/combat tutorial
5. Memory Crystal
6. Naris First Whisper
7. Ash Gate
8. Celestial Wolf
9. Bone Beast boss
10. Demo End
11. save/load round trip
12. EN/AR UI pass
13. Windows Development build
14. no blocking crash in full run
15. performance capture attached to QA report

## v2.1 — Final Art Pass

- Ashen Vessel production character
- Celestial Wolf production companion
- Bone Beast production boss
- Ashen Forest modular environment kit
- hero weapons
- final UI iconography
- Niagara VFX
- materials, LOD/HLOD, collision and optimization

## v2.2 — Audio + Cinematic Pass

- main theme
- exploration ambience
- combat theme
- boss theme
- foley/weapon/UI SFX
- wolf/boss creature audio
- cinematic VO
- final teaser/gameplay capture

## v2.3 — Packaging + QA

- Windows Development
- Windows Shipping
- crash/error logging
- controller pass
- save migration test
- localization regression
- performance budgets
- release-candidate checklist

## v2.4 — Store + Marketing Kit

- Steam page content
- screenshots/capsules
- trailer
- press kit
- privacy/terms where applicable
- public demo package only after gate approval

## Immediate engineering order

1. Player actor + Enhanced Input + camera/lock-on.
2. Weapon hit detection + combat montage windows.
3. Bone Beast playable boss implementation.
4. UMG HUD and menu flow.
5. Quest/inventory/dialogue wiring in one W04 map.
6. Celestial Wolf commands and Echo Link.
7. AssetForge → Unreal import bridge proof-of-concept.
8. Windows package automation and smoke test.

A system is not complete until **Data → Runtime → UI → Save → QA** works together.
