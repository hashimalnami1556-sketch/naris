# CALL OF NARIS — Vertical Slice Production Audit

**Date:** 2026-10-01
**Runtime owner:** Unreal Engine 5
**Vertical slice:** W04 — Ashen Forest
**Status:** Production foundation / not Release Candidate

## Canonical slice
Main Menu → Awakening → Forest Entrance → Combat Tutorial → Broken Shrine / Memory Crystal → First Whisper → Ash Gate → Celestial Wolf → Ruined Bridge → Bone Beast Arena → Bone Beast → Reward → Demo End.

## Confirmed production foundation
- Canonical Unreal W04 project and build/package scripts exist.
- Ashen Vessel, Celestial Wolf, Bone Beast, Ash Gate, Waystone and Memory Crystal have repository identities/contracts.
- Combat, boss, presentation, material, animation, localization and validation layers exist in source/specification form.
- Blender → validation → Unreal exchange tooling exists.
- Production asset registry is authoritative; statuses must not be promoted without evidence.

## P0 — blockers before Vertical Slice RC
1. Final Ashen Vessel production animation set and validated montage bindings.
2. Animation-driven combat hit windows, hit/hurt boxes, combo buffering, parry timing and lock-on acceptance.
3. Final rigged Celestial Wolf runtime asset with locomotion, roar, attack and summon/despawn presentation.
4. Final rigged Bone Beast runtime asset with phase-specific attacks, telegraphs, reactions, phase transitions and death.
5. Ashen Forest production collision/NavMesh/traversal pass.
6. Runtime audio payloads: combat, wolf, Bone Beast, ambience and music.
7. Runtime Niagara/VFX payloads for hero, wolf, boss and environment.
8. Deterministic save/load for required W04 world state.
9. Controller production pass and input glyph behavior.
10. Unreal Editor import/smoke test, full playthrough, profiling and Win64 packaged-build evidence.

## P1 — publisher / Steam presentation
- Production HUD and menus.
- Camera collision, lock-on framing, boss framing and impact feedback.
- Environment dressing, landmarks, decals, foliage, fog and lighting zones.
- Opening, wolf reveal and Bone Beast intro/death cinematics.
- Accessibility and settings.
- Localization/RTL acceptance.
- Performance budgets and regression suite.

## Scope control
Do not expand to additional worlds, large crafting systems, multiplayer, or large enemy/weapon catalogs until W04 passes RC gates.

## Evidence rule
A file, script, concept, registry entry or successful compile is not by itself proof of a finished runtime feature. Promotion to `qa`, `approved` or `release` requires engine evidence and acceptance results.

## Next execution order
Combat architecture → hero animations → wolf → Bone Beast → W04 collision/NavMesh → audio/VFX → HUD/camera → save/load → cinematics → controller/accessibility → profiling → Win64 package → QA.
