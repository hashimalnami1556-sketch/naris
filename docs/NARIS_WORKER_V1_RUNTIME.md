# NARIS Worker v1 Runtime Contract

## Purpose

Connect the NARIS MCP job system to Blender through a constrained, auditable protocol.

## Envelope

`protocol = naris-worker/v1`

Each request contains `jobId`, an optional `assetId`, one named `operation`, and a JSON `parameters` object.

## Allowed operations

- `VALIDATE_ASSET`
- `BUILD_ASSET`
- `GENERATE_LOD`
- `GENERATE_COLLISION`
- `PROCESS_TEXTURES`
- `RENDER_PREVIEW`
- `EXPORT_ASSET`

## Security boundary

The worker never accepts or evaluates arbitrary Python source from MCP/AI. Each operation must map to an explicitly registered Blender/NARIS Toolkit operator.

## Event lifecycle

`QUEUED → RUNNING → SUCCEEDED | FAILED | CANCELLED`

Progress is an integer from 0 to 100. Runtime success is valid only when the worker emits a terminal event and provides artifact/validation evidence where applicable.

## Implementation

- TypeScript envelope adapter: `mcp/src/worker-runtime.ts`
- Blender dispatcher: `blender/naris_toolkit/worker/naris_worker_v1.py`
- Stable protocol types: `mcp/src/worker-protocol.ts`

## Transport

The contract is transport-neutral. Supported future transports include local stdio, localhost HTTP, or a named pipe. Transport selection must not weaken the permission boundary.
