# CALL OF NARIS

Production repository for **CALL OF NARIS**, a dark-fantasy action RPG built around ten fractured worlds, modular environments, cinematic storytelling, tactical combat, and a controlled AAA-style asset pipeline.

## Repository structure

- `docs/` — production, architecture, naming, and pipeline documentation.
- `worlds/` — world-specific environment specifications.
- `data/` — machine-readable registries and metadata.
- `tools/` — future pipeline utilities and automation.

## Core production principle

Every production asset receives one immutable NARIS Asset ID and is traceable from concept/design through source art, registry, Unreal integration, QA, and approval.

## Current environment scope

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

## External production systems

- **Figma / Product Design** — UX, UI, design systems, gameplay-flow specifications.
- **Adobe / Adobe Express** — concept art, visual assets, marketing creative, texture references.
- **Adobe Acrobat** — production bibles and controlled PDF documentation.
- **Adalo** — operational asset registry and production tracking.
- **GitHub** — source control, documentation, automation, review, and release history.
- **Unreal Engine** — runtime, world building, materials, Niagara VFX, lighting, streaming, and final game build.
- **PostHog** — telemetry and product/gameplay analytics during playable testing.

See `docs/INTEGRATION_ARCHITECTURE.md` for the integration contract and `docs/ASSET_NAMING.md` for the canonical asset-ID system.
