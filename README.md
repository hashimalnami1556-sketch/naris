# CALL OF NARIS

> **Canonical production repository** for *CALL OF NARIS* — a dark-fantasy action RPG built around ten fractured worlds, modular environments, cinematic storytelling, tactical combat, and a controlled AAA-style asset pipeline.

## Repository status

- **Default branch:** `main`
- **Production source of truth:** GitHub
- **Primary engine target:** Unreal Engine 5.4+
- **Primary platform target:** Windows PC
- **Primary vertical slice:** W04 — Ashen Forest
- **Canonical asset registry:** `data/MASTER_ASSET_REGISTRY.json`
- **Canonical pipeline:** `docs/MASTER_PRODUCTION_PIPELINE.md`
- **Repository map:** `docs/REPOSITORY_MAP.md`
- **Production status:** `docs/PRODUCTION_STATUS.md`
- **Master integration spec:** `docs/production/NARIS_MASTER_INTEGRATION_v1_9.md`
- **World generation tool:** `tools/assetforge/world_generator.py`

## Current integration level — 2026-09-22

The repository has moved beyond isolated prototype packages. The current production baseline is **v1.9 Master Integration**, with Unreal/W04 as the canonical implementation path.

| Layer | Scope |
|---|---|
| v1.3 | Visual identity, branding, English-first production baseline |
| v1.4 | Combat, energy, abilities, poise, HUD contracts |
| v1.5 | World interaction, quests, inventory, dialogue |
| v1.6 | Companion, crafting, map, AI director, factions, world events |
| v1.7 | Bosses, cinematics, localization, settings, build/QA contracts |
| v1.8 | GameRoot/demo loop, save slots, achievements, release gates |
| v1.9 | Master merge, platform packaging, playtest, validation, PC-first consolidation |

The public demo gate remains closed until the playable W04 loop passes engine, performance and QA acceptance.

## Canonical structure

    naris/
    ├── .github/                         # CI/CD and repository automation
    ├── docs/                            # Canonical production documentation
    ├── data/                            # Machine-readable registries and manifests
    ├── GAME_STUDIO/                     # Playable slices and game prototypes
    ├── NARIS_MASTER/                    # Master production workspace
    ├── unreal/                          # Unreal Engine bootstrap/runtime project
    ├── assets/                          # Approved/source asset packages
    ├── apps/                            # Supporting applications/tools
    ├── source/                          # Runtime/source code
    ├── tools/                           # Production automation and AssetForge
    ├── schemas/                         # JSON/schema contracts
    ├── mcp/                             # MCP integration layer
    ├── migration/                       # Migration and normalization utilities
    ├── generated_designs/               # Generated visual/design references
    └── DOCUMENTS/                       # Historical/source material; not canonical

## Production rule

The repository is organized around a single traceability chain:

`BRIEF → CONCEPT → APPROVAL → ASSET_ID → SOURCE → MODEL/ART → MATERIAL → RIG/ANIMATION → ENGINE → OPTIMIZATION → QA → APPROVED → RELEASE`

A generated image is a **reference**, not a finished game asset. Assets become release candidates only after technical-art, engine, performance, gameplay and QA gates are satisfied.

## Asset identity

Every production asset receives one immutable ID using:

`NARIS-W<world>-<domain>-<type>-<sequence>`

Examples:

- `NARIS-W04-CHR-HERO-0001`
- `NARIS-W04-ENV-KIT-0001`
- `NARIS-W04-WPN-MACE-0001`
- `NARIS-W04-VFX-EMBER-0001`

## Worlds

| ID | World | Signature |
|---|---|---|
| W01 | Frozen Peaks | Ice, avalanches, frozen ruins |
| W02 | Forge of Flame | Volcanic industry, molten metal |
| W03 | Echoes Desert | Dunes, buried cities, sound anomalies |
| W04 | Ashen Forest | Ash, ruins, mist, corrupted wildlife |
| W05 | Silent Abyss | Deep darkness, pressure, bioluminescence |
| W06 | Inverted Towers | Impossible architecture, gravity shifts |
| W07 | Lost Souls Swamp | Spectral wetlands, drowned ruins |
| W08 | Astral Fortress | Celestial stone, void bridges, star energy |
| W09 | Forgotten Canals | Ancient waterways, machinery, flooded districts |
| W10 | Throne of Naris | Royal ruins, cosmic corruption, final citadel |

## Production domains

`CHR` Characters · `ENM` Enemies · `BOS` Bosses · `WPN` Weapons · `PRP` Props · `ENV` Environment · `MAT` Materials · `VFX` Visual Effects · `UI` Interface · `MAP` Maps · `CINE` Cinematics · `AUD` Audio · `QST` Quests/Content

## AssetForge world layer

`tools/assetforge/world_generator.py` is the deterministic engine-neutral world-data generator. It currently provides:

- 99 biome identifiers
- heightmap generation
- moisture/temperature fields
- biome assignment
- downhill river guides
- settlement placement
- deterministic road guides
- streaming chunk metadata
- JSON export for Unreal import tooling

Fast validation:

    cd tools/assetforge
    python -m unittest test_world_generator.py

Generate a sample:

    python world_generator.py --size 256 --chunk-size 32 --output build/worldgen/naris_world.json

## Unreal / Windows PC target

Canonical bootstrap project:

`unreal/NARIS_W04/NARIS_W04.uproject`

The next executable milestone is a 10–15 minute W04 PC vertical slice:

`Main Menu → Intro → Wake Area → Movement/Combat → Memory Crystal → First Whisper → Ash Gate → Celestial Wolf → Bone Beast → Demo End`

## Visual standard

Dark Fantasy + High Fantasy + Cinematic AAA presentation with deliberate color contrast.

Core visual accents:

- Naris Fire — Ember Orange
- Aether — Royal Violet
- Spirit Energy — Mist Cyan
- Ancient Power — Ancient Gold
- Base world tone — Ash Blue / Obsidian

## Documentation entry points

- `docs/MASTER_PRODUCTION_PIPELINE.md`
- `docs/REPOSITORY_MAP.md`
- `docs/PRODUCTION_STATUS.md`
- `docs/production/NARIS_MASTER_INTEGRATION_v1_9.md`
- `docs/production/ASSETFORGE_WORLDGEN.md`
- `data/MASTER_ASSET_REGISTRY.json`
- `data/manifests/MASTER_INTEGRATION_2026-09-22.json`
