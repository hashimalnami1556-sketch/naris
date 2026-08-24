# CALL OF NARIS — COMPLETE REPOSITORY ARCHITECTURE

This repository is the single source of truth for NARIS production.

## Layers
- `NARIS_MASTER/` — design, production specifications and manifests
- `GAME/UNREAL/` — Unreal Engine project source
- `ASSETS/CHARACTERS/` — character references and production assets
- `ASSETS/ENVIRONMENTS/` — world and environment assets
- `ASSETS/CONCEPTS/` — concept/reference art
- `ASSETS/CINEMATICS/` — cinematic source material
- `ASSETS/MARKETING/` — promotional assets
- `DOCUMENTS/` — project documents and PDFs
- `ARCHIVE/` — generated snapshots and historical packages

## Binary policy
Large binary assets must be tracked with Git LFS or an equivalent large-file workflow. The repository must never pretend that a text manifest is the binary asset itself.

## Production rule
Every asset must have an inventory record with source filename, type, size, SHA-256, destination path, and status.
