# NARIS Integration Architecture

## Objective

Create a single traceable production chain across design, visual production, asset management, source control, Unreal Engine integration, and telemetry.

## System of record

GitHub is the canonical versioned record for project specifications, schemas, pipeline definitions, and automation. Adalo is the operational asset registry. Figma/Product Design owns interaction and UX specifications. Adobe tools own visual production and marketing source material. Unreal Engine owns runtime implementation.

## Asset lifecycle

Concept → Design → Asset ID → Source Art → Registry → Unreal Import → Integration → QA → Approved → Release.

## Canonical Asset ID

`NARIS-W<world>-<domain>-<type>-<sequence>`

Example: `NARIS-W06-ENV-GEO-0001`

The same ID should appear in the Adalo registry, Figma reference, Adobe source/export metadata where practical, GitHub documentation, and Unreal asset metadata.

## Domains

- `ENV` — environment
- `CHR` — character
- `WPN` — weapon
- `PROP` — prop
- `MAT` — material
- `VFX` — visual effects
- `SFX` — sound
- `UI` — interface
- `CINE` — cinematics
- `QUEST` — quest/content

## Production gates

1. Concept
2. Approved concept
3. Blockout
4. High Poly
5. Retopo
6. UV
7. Texture
8. Material
9. Unreal Integration
10. Optimization
11. QA
12. Approved

## Tool responsibilities

| System | Responsibility |
|---|---|
| Product Design | UX, interaction, gameplay flow, design validation |
| Figma | UI/UX and design system source |
| Adobe | Concept art, visual assets, textures and source art |
| Adobe Express | Marketing and social creative |
| Adobe Acrobat | Controlled production PDFs and bibles |
| Adalo | Operational asset registry, ownership, status and completeness |
| GitHub | Versioned specifications, code, automation and review history |
| Unreal Engine | Runtime implementation, world, materials, Niagara, lighting and build |
| PostHog | Testing telemetry and gameplay/product analytics |

## Environment codes

W01 Frozen Peaks
W02 Forge of Flame
W03 Echoes Desert
W04 Ashen Forest
W05 Silent Abyss
W06 Inverted Towers
W07 Lost Souls Swamp
W08 Astral Fortress
W09 Forgotten Canals
W10 Throne of Naris

## Integration rule

No production asset should be considered release-ready unless its Asset ID, source, version, production stage, Unreal integration state, optimization state, and QA state are traceable.
