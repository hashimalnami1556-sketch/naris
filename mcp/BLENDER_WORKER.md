# NARIS Blender Worker v1.0

## Purpose
The Blender Worker is the controlled execution boundary between NARIS MCP and Blender.

## Security rule
The worker MUST NOT expose arbitrary Python execution to an AI agent.

## Allowed operations
- VALIDATE_ASSET
- BUILD_ASSET
- GENERATE_LOD
- GENERATE_COLLISION
- PROCESS_TEXTURES
- RENDER_PREVIEW
- EXPORT_ASSET

## Job lifecycle
QUEUED -> RUNNING -> SUCCEEDED
QUEUED -> CANCELLED
RUNNING -> FAILED
RUNNING -> CANCELLED
Any operation that needs human authorization -> REQUIRES_APPROVAL

## Worker contract
Input:
- job_id
- asset_id
- operation
- pipeline/profile
- validated parameters

Output:
- job_id
- status
- progress
- artifacts
- validation summary
- errors
- warnings

## Required safeguards
1. Validate Asset ID before loading an asset.
2. Restrict filesystem access to the NARIS workspace.
3. Never overwrite canonical source assets silently.
4. Write generated outputs to generated/export areas.
5. Run required validation before export.
6. Emit structured errors.
7. Record audit metadata for mutations.
8. Preserve source and create recoverable versions before destructive changes.

## Runtime implementation target
Blender 4.x + Python 3.11+.

The MCP server owns authorization and job creation. The Blender add-on owns Blender-specific execution. The transport between them is an adapter and may be implemented with localhost IPC, a local HTTP endpoint, a socket, or another controlled transport.

## Current state
The repository contains the job and worker contracts. Actual Blender IPC is intentionally NOT claimed as connected until an integration test proves it.
