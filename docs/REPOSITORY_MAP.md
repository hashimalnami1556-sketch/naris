# CALL OF NARIS — Repository Map

## 1. Canonical rule

`main` is the canonical integration branch. GitHub is the versioned source of truth for production specifications, registries, schemas, manifests, automation and release history.

## 2. Directory ownership

| Directory | Role | Canonical? |
|---|---|---|
| `.github/` | CI/CD, validation and repository automation | Yes |
| `docs/` | Production and technical documentation | Yes |
| `data/` | Registries, schemas and machine-readable manifests | Yes |
| `source/` | Runtime/application source | Yes |
| `schemas/` | Data contracts and validation schemas | Yes |
| `assets/` | Approved/source asset packages | Yes |
| `GAME_STUDIO/` | Playable slices and production prototypes | Yes |
| `NARIS_MASTER/` | Master production workspace | Yes |
| `mcp/` | MCP/integration code | Yes |
| `apps/` | Supporting applications | Yes |
| `migration/` | Migration and normalization utilities | Yes |
| `generated_designs/` | Generated design references | Controlled/reference only |
| `DOCUMENTS/` | Historical/source notes and imported material | Archive/source only |

## 3. Documentation taxonomy

Use these subdirectories under `docs/` for new canonical documentation:

- `architecture/` — runtime, integration and system architecture.
- `production/` — production pipeline, asset standards, naming and QA.
- `worlds/` — world bibles, regional specifications and environment plans.
- `characters/` — character bibles and gameplay/readability specifications.
- `environments/` — modular kit standards, materials, LOD and collision rules.
- `ui/` — HUD, menus, UX flows and design-system contracts.
- `release/` — release candidates, build checklists and change logs.

Existing root-level documents remain valid. New documents should use the taxonomy above rather than introducing additional top-level documentation folders.

## 4. Asset traceability

Every asset must be represented in `data/MASTER_ASSET_REGISTRY.json` before entering a production gate.

Required traceability:

`brief → concept → approval → asset_id → source → production → engine → optimization → qa → approved → release`

## 5. Naming

Use lowercase kebab-case for documentation filenames unless an existing canonical filename is already established. Use the NARIS Asset ID format for production assets:

`NARIS-W<world>-<domain>-<type>-<sequence>`

## 6. Generated content policy

Generated images, videos and 3D conversions are references or source candidates until they receive an Asset ID and pass the relevant technical-art and QA gates. Do not treat `generated_designs/` as an approved runtime asset library.

## 7. Historical material

`DOCUMENTS/` is retained to preserve provenance. It is not the authoritative location for current production decisions. When a historical note becomes a current requirement, promote the requirement into `docs/` and reference the originating material.

## 8. Future normalization

The repository can later migrate legacy documents and duplicate prototypes into the canonical taxonomy. Such migration must be performed as traceable commits and must not delete source material without a provenance record.
