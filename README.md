# CALL OF NARIS

> **Canonical production repository** for *CALL OF NARIS* — a dark-fantasy action RPG built around ten fractured worlds, modular environments, cinematic storytelling, tactical combat, and a controlled AAA-style asset pipeline.

## Repository status

- **Default branch:** `main`
- **Production source of truth:** GitHub
- **Canonical asset registry:** `data/MASTER_ASSET_REGISTRY.json`
- **Canonical pipeline:** `docs/MASTER_PRODUCTION_PIPELINE.md`
- **Repository map:** `docs/REPOSITORY_MAP.md`
- **Production status:** `docs/PRODUCTION_STATUS.md`

## Canonical structure

```text
naris/
├── .github/                         # CI/CD and repository automation
├── docs/                            # Canonical production documentation
│   ├── architecture/                # System and technical architecture
│   ├── production/                  # Pipeline, standards and gates
│   ├── worlds/                      # World bibles and world specifications
│   ├── characters/                  # Character specifications
│   ├── environments/                # Environment production specifications
│   ├── ui/                          # UI/UX specifications
│   └── release/                     # Release notes and checklists
├── data/                            # Machine-readable registries and manifests
│   ├── MASTER_ASSET_REGISTRY.json   # Asset IDs, status and ownership metadata
│   └── manifests/                   # Batch and delivery manifests
├── GAME_STUDIO/                     # Playable slices and game prototypes
├── NARIS_MASTER/                    # Master production workspace
├── assets/                          # Approved/source asset packages
├── apps/                            # Supporting applications/tools
├── source/                          # Runtime/source code
├── schemas/                         # JSON/schema contracts
├── mcp/                             # MCP integration layer
├── migration/                       # Migration and normalization utilities
├── generated_designs/               # Generated visual/design references
└── DOCUMENTS/                       # Historical/source material; not canonical
```

## Production rule

The repository is organized around a single traceability chain:

`BRIEF → CONCEPT → APPROVAL → ASSET_ID → SOURCE → MODEL/ART → MATERIAL → RIG/ANIMATION → ENGINE → OPTIMIZATION → QA → APPROVED → RELEASE`

A generated image is a **reference**, not a finished game asset. Assets become release candidates only after technical-art, engine, performance, and QA gates are satisfied.

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

## External production systems

Figma, Adobe, Adobe Acrobat, Adalo, Unreal Engine, PostHog, CreativeClaw, Apixel, OpenArt, Higgsfield, to3D, Visla, VideoZero and Slack are treated as specialized production systems. GitHub remains the versioned source of truth for specifications, schemas, manifests, automation definitions, review history and release records.

## Visual standard

Dark Fantasy + High Fantasy + Cinematic AAA presentation with deliberate color contrast. Core visual accents: Naris Fire, Aether Violet, Mist Cyan and Ancient Gold.

## Current revision

The horned enemy variant is being developed with substantially shorter horns, a heavy demonic tail, and a brutal mace/club while preserving the established armor language, anatomy, materials and silhouette.

## Documentation entry points

- `docs/MASTER_PRODUCTION_PIPELINE.md`
- `docs/REPOSITORY_MAP.md`
- `docs/PRODUCTION_STATUS.md`
- `data/MASTER_ASSET_REGISTRY.json`
