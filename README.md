# CALL OF NARIS

Production repository for **CALL OF NARIS**, a dark-fantasy action RPG built around ten fractured worlds, modular environments, cinematic storytelling, tactical combat, and a controlled AAA-style asset pipeline.

## Repository structure

- `docs/` — production, architecture, naming, and pipeline documentation.
- `worlds/` — world-specific environment specifications.
- `data/` — machine-readable registries and metadata.
- `tools/` — future pipeline utilities and automation.

## Canonical production record

GitHub is the versioned source of truth for production specifications, schemas, manifests, automation definitions, and release history. Every production asset receives one immutable NARIS Asset ID and is traceable from concept/design through source art, engine integration, QA, and approval.

See:

- `docs/INTEGRATION_ARCHITECTURE.md`
- `docs/MASTER_PRODUCTION_PIPELINE.md`
- `docs/ASSET_NAMING.md`
- `data/MASTER_ASSET_REGISTRY.json`

## Current world scope

1. Frozen Peaks
2. Forge of Flame
3. Echoes Desert
4. Ashen Forest
5. Silent Abyss
6. Inverted Towers
7. Lost Souls Swamp
8. Astral Fortress
9. Forgotten Canals
10. Throne of Naris

## Production domains

Characters, enemies, bosses, weapons, props, environments, materials, VFX, UI/UX, maps, cinematics, audio, quests/content, marketing.

## External production systems

- **Figma / Product Design** — UX, UI, design systems, gameplay-flow specifications.
- **Adobe / Adobe Express** — concept art, visual assets, marketing creative, texture references.
- **Adobe Acrobat** — controlled production PDFs and bibles.
- **Adalo** — operational asset registry and production tracking.
- **GitHub** — source control, documentation, automation, review, and release history.
- **Unreal Engine** — runtime, world building, materials, Niagara VFX, lighting, streaming, and final game build.
- **PostHog** — telemetry and product/gameplay analytics during playable testing.
- **CreativeClaw / Apixel / OpenArt / Higgsfield** — controlled concept, character, environment, key-art and cinematic generation.
- **to3D** — approved 2D concept to 3D starting-asset conversion.
- **Visla / VideoZero** — marketing and motion-graphics production where applicable.
- **Slack** — production coordination and decision log.

## Visual standard

Dark Fantasy + High Fantasy + Cinematic AAA presentation, with rich color contrast. Primary accents are Naris Fire, Aether Violet, Mist Cyan, and Ancient Gold. Final assets must not rely on gray-only presentation.

## Current character revision

The supplied horned enemy reference is being developed as a controlled variant with substantially shorter horns, a heavy demonic tail, and a brutal mace/club while preserving the established armor language, anatomy, materials, and silhouette.
