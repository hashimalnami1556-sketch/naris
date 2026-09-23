# CALL OF NARIS — Production Status

**Snapshot:** 2026-09-23
**Canonical engine path:** Unreal Engine 5.4+  
**Primary target:** Windows PC  
**Primary vertical slice:** W04 — Ashen Forest  
**Release gate:** Internal playtest only

## Repository baseline

- Canonical branch: `main`
- Asset registry: `data/MASTER_ASSET_REGISTRY.json`
- Production pipeline: `docs/MASTER_PRODUCTION_PIPELINE.md`
- Repository governance: `docs/REPOSITORY_MAP.md`
- Unreal bootstrap: `unreal/NARIS_W04/NARIS_W04.uproject`
- Master integration: `docs/production/NARIS_MASTER_INTEGRATION_v1_9.md`
- AssetForge world generator: `tools/assetforge/world_generator.py`

## Integration status

| Layer | Status | Canonical role |
|---|---|---|
| v1.3 | Integrated as design baseline | Visual identity, branding, color system |
| v1.4 | Contracted into Unreal path | Combat, energy, abilities, poise |
| v1.5 | Contracted into Unreal path | Quests, inventory, dialogue, interaction |
| v1.6 | Contracted into Unreal path | Companion, crafting, map, AI director |
| v1.7 | Contracted into Unreal path | Boss, cinematic, localization, settings, build/QA |
| v1.8 | Consolidated | GameRoot, demo loop, save slots, achievements |
| v1.9 | Active | Master merge, PC packaging, playtest, validation |

Earlier Godot-oriented packages remain useful as design/system provenance, but **Unreal Engine W04 is the canonical implementation target**.

## Active production focus — W04 Ashen Forest

### Playable loop

1. Main Menu
2. Intro cinematic
3. Wake Area
4. Movement/combat tutorial
5. Memory Crystal pickup
6. Naris First Whisper dialogue
7. Ash Gate interaction
8. Celestial Wolf encounter/link
9. Bone Beast boss encounter
10. Demo End screen

### Runtime systems required for acceptance

- Third-person player controller
- Enhanced Input
- camera + lock-on
- health / poise / stagger / execution
- five-essence runtime
- weapon hit detection
- companion commands + Echo Link
- quest/inventory/dialogue state
- checkpoint/save/load
- boss phase controller
- UMG HUD
- audio buses
- localization (EN/AR)
- Windows packaging
- automated smoke/validation tests

## World / AssetForge layer

A deterministic world-data generator is now part of the repository.

Current output layers:

- heightmap
- 99-biome catalog and biome grid
- river guide splines
- settlement points
- road guide splines
- streaming chunk metadata

The generator is engine-neutral; Unreal remains authoritative for final Landscape, PCG, splines, World Partition and authored gameplay spaces.

## Art status

The registry still intentionally distinguishes concept/blockout from release-ready assets.

Priority final-art replacements:

- Ashen Vessel final production model
- Celestial Wolf final production model
- Bone Beast final boss model
- Ashen Forest modular kit
- final HUD/UI
- final weapon set
- final Niagara VFX
- production animation set
- music/SFX/voiceover

## Gate policy

`concept`, `brief`, and `blockout` do **not** mean production-ready.

An asset can enter `approved` only after:

1. Visual approval
2. Technical-art validation
3. Engine integration
4. collision/LOD validation
5. performance validation
6. gameplay validation where applicable
7. QA sign-off
8. registry update

## Public demo gate

Public distribution remains disabled until all blocking conditions pass:

- W04 loop playable end-to-end
- no blocking crashes
- input + controller profile stable
- save/load round-trip verified
- boss encounter completable
- EN/AR text pass complete
- Windows package validated
- performance budget accepted
- asset licensing/provenance recorded
- QA release checklist green

## Next production pass

1. Finish Unreal player/companion/boss actor wiring.
2. Import AssetForge W04 world data into PCG/Landscape test tooling.
3. Build one complete W04 level rather than disconnected test scenes.
4. Replace combat placeholders with real montages/hit windows.
5. Complete UMG HUD and menu flow.
6. Add Windows Development/Shipping build automation.
7. Run 10–15 minute internal playtest and log defects.
8. Promote only verified assets/statuses in the master registry.

## Shared knowledge and source repair — 2026-09-23

The shared agent entry point is [AGENTS.md](../AGENTS.md), with current work in [PROJECT_STATE.md](../PROJECT_STATE.md). Duplicate Unreal target definitions and module registration were removed, static guards were added, and AssetForge zero-count behavior was repaired. Repository validation and 10 Python tests pass locally. No Unreal compilation, Claude Code session, editor playtest or Windows package was executed here. See the [updated gap register](PROJECT_GAP_REGISTER.md).
