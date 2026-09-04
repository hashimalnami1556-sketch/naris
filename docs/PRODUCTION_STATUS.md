# CALL OF NARIS — Production Status

**Snapshot:** 2026-09-04

## Repository baseline

- Canonical branch: `main`
- Asset registry: `data/MASTER_ASSET_REGISTRY.json`
- Production pipeline: `docs/MASTER_PRODUCTION_PIPELINE.md`
- Repository governance: `docs/REPOSITORY_MAP.md`

## Current asset registry snapshot

The registry currently tracks characters, enemies, bosses, weapons, environment kits, materials, VFX, UI, maps and cinematics across the ten worlds.

## Active production focus

### W04 — Ashen Forest

Primary playable-slice focus. Current tracked items include:

- Ashen Vessel
- Celestial Wolf
- Ash Wanderer
- Translucent Hero variant
- Gate Guardian
- Bone Beast
- Fallen Warden
- Ashen Forest Modular Kit
- Waystone
- Holy Portal
- Ashen Stone Tile
- Naris Fire Ember System
- Celestial Spirit FX
- Combat HUD
- Ashen Forest Region Map
- The Gate Remembers teaser

### Cross-world production

Modular environment kits are defined for W01–W10. Core weapon and enemy families are also registered across the relevant worlds.

## Gate policy

Current registry states are intentionally conservative. `concept`, `brief`, and `blockout` do **not** mean production-ready.

An asset can enter `approved` only after:

1. Visual approval
2. Technical-art validation
3. Engine integration
4. Collision/LOD validation
5. Performance validation
6. Gameplay validation where applicable
7. QA sign-off
8. Registry update

## Next organization pass

1. Move new documentation into the `docs/` taxonomy.
2. Add batch manifests under `data/manifests/` for each production batch.
3. Keep `DOCUMENTS/` as provenance/archive rather than a second source of truth.
4. Keep generated visual references separated from approved runtime assets.
5. Require Asset IDs for new production deliveries.
6. Keep CI validation enabled for registry/schema integrity.
