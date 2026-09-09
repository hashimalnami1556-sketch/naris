# NARIS BioNeMo Agent Foundation

A production-oriented scientific AI sidecar for the NARIS repository. It is intentionally isolated from the game runtime.

## First vertical slice

`Protein sequence → validation → NVIDIA BioNeMo OpenFold3 NIM → structured result`

The service supports NVIDIA's hosted NIM endpoint first, avoiding a local GPU deployment dependency. A local NIM can be introduced later behind the same adapter.

## Architecture

- `api/` — FastAPI service
- `agent/` — routing and workflow orchestration
- `integrations/bionemo/` — NVIDIA NIM adapters
- `schemas/` — strict request/result models
- `web/` — React/Vite client (next implementation step)

## Security

Never commit `NGC_API_KEY`. Use environment variables or a secret manager.
