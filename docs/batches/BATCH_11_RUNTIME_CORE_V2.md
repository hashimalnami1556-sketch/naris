# NARIS — Batch 11: Runtime Integration Core v2

**Status:** IMPLEMENTED / awaiting CI and browser QA

## Implemented
- React 19 + Babylon.js + TypeScript browser runtime scaffold.
- Explicit simulation boundary through `GameStateStore`.
- Typed `GameBus` for gameplay events.
- `ServiceRegistry` for runtime dependencies.
- Unified `CharacterController` for Ash / Rune / Kor.
- Combat runtime with three enemy archetypes, chase, attack cooldown and hit resolution.
- Ashen Forest hero scene with gate, environmental dressing and combat encounters.
- RTL cinematic HUD and responsive mobile presentation.
- Strict TypeScript/Vite configuration.

## Acceptance gates
- [x] Runtime architecture separated from DOM HUD.
- [x] Character switching is event-driven.
- [x] Player attacks resolve against nearest valid enemy.
- [x] Enemy chase/attack loop exists.
- [x] Game state is serializable independently from renderer objects.
- [x] Mobile viewport CSS is included.
- [ ] `pnpm build` / CI confirmation.
- [ ] Browser screenshot and interaction QA.
- [ ] Replace procedural geometry with approved production GLB assets.
- [ ] Waystone/save/quest/shard/boss/companion integration.

## Important production note
Procedural geometry is intentionally limited to this integration scaffold. It is not accepted as final visual production art. The existing asset registry and production sheets remain the source of truth for the art pipeline.
