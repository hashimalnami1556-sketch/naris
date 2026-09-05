# NARIS Evidence Model v1

## Purpose

NARIS runtime success is evidence-bound. A worker response alone is not a release claim.

Canonical chain:

`Job → Worker Event → Artifact → Validation Evidence → Audit Record → Release Decision`

## Artifact record

Each verified runtime artifact records:

- immutable `artifactId`
- source `jobId`
- optional `assetId`
- artifact `kind`
- repository-relative `path`
- byte size when available
- SHA-256 when available
- creation timestamp
- `verified=true` only after the worker result points to an existing file

## Audit record

Audit records capture action, job, asset, terminal status, artifact IDs, and evidence references. Secrets, tokens, credentials, authorization headers, and arbitrary worker payloads are never persisted by the evidence layer.

## Success rule

`SUCCEEDED` means the controlled Blender Worker returned a successful terminal event. For operations that produce files, release readiness additionally requires a verified artifact. Validation operations require validation evidence before a release decision.

A missing worker transport results in `BLOCKED`, never synthetic success.

## Storage

Runtime evidence is persisted under `data/` as JSON during v1. This is an implementation baseline; production deployments may replace the store with an append-only database/object store without changing the record contract.

## Security boundary

The evidence layer records metadata and cryptographic hashes only. It does not execute Blender code, accept arbitrary Python, or store secrets.
