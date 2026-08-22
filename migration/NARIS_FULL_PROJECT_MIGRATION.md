# NARIS Full Project Migration

## Target
`hashimalnami1556-sketch/naris`

## Migration status
The repository is the canonical source of truth for the project. This migration record documents the external attachment pack prepared from files physically available in the ChatGPT runtime.

## Pack
`NARIS_FULL_PROJECT_MIGRATION.zip`

The pack contains 32 physically accessible project-related files plus a SHA-256 manifest.

## Repository organization

- `docs/` — design, technical and production documentation
- `assets/` — art references and production assets
- `archive/` — historical v1.x snapshots/packages
- `mcp/` — MCP orchestration layer
- `migration/` — migration records and manifests

## Important limitation
Some historical ChatGPT File Library attachments are references that are not mounted as binary files in the current runtime. They cannot be honestly represented as transferred binaries until they are made available to the execution environment.

## Integrity
The local migration pack includes `inventory/MIGRATION_MANIFEST.json` with SHA-256 hashes for every copied file.

## Production rule
Do not delete historical source material during migration. Preserve provenance and Asset IDs. Unreal Engine remains the production runtime; MCP remains the orchestration layer.
