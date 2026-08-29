# NARIS MCP v1.0 — Specification

## Purpose
Provide a controlled, evidence-backed MCP interface for CALL OF NARIS production. MCP is the orchestration layer between an AI agent, the NARIS production repository, the NARIS Blender Worker, validation pipelines, and future WebMCP/MCP App surfaces.

## Runtime boundary
- Unreal Engine remains the production runtime.
- Blender is an asset-production runtime/worker.
- MCP MUST NOT expose unrestricted Blender Python, shell execution, credentials, or unrestricted filesystem/network access.
- WebMCP and MCP App MUST use the same authorization and validation gates.

## Core lifecycle
DISCOVER -> INSPECT -> ANALYZE -> BUILD -> VALIDATE -> EXPORT -> REPORT -> APPROVE

## Canonical Asset ID
`NARIS-W<world>-<domain>-<type>-<sequence>`

Worlds: W01 Frozen Peaks, W02 Forge of Flame, W03 Echoes Desert, W04 Ashen Forest, W05 Silent Abyss, W06 Inverted Towers, W07 Lost Souls Swamp, W08 Astral Fortress, W09 Forgotten Canals, W10 Throne of Naris.

Domains: ENV, CHR, WPN, PROP, MAT, VFX, SFX, UI, CINE, QUEST.

Asset IDs are immutable.

## v1.0 tools
### Read
- `naris.project.status`
- `naris.project.get_settings`
- `naris.asset.list`
- `naris.asset.search`
- `naris.asset.get`
- `naris.asset.inspect`
- `naris.job.status`
- `naris.report.get`

### Analyze / QA
- `naris.validation.run`
- `naris.validation.get_report`
- `naris.validation.list_failures`
- `naris.asset.analyze`
- `naris.report.generate`

### Controlled mutation (phase 2)
- `naris.asset.build`
- `naris.asset.generate_lod`
- `naris.asset.generate_collision`
- `naris.texture.process`
- `naris.material.validate`
- `naris.asset.export`
- `naris.job.cancel`

Phase-2 tools MUST NOT be enabled until permission, job, audit, and validation contracts are implemented.

## Permission levels
- READ: repository/project/asset inspection
- ANALYZE: validation and reports
- BUILD: deterministic asset pipelines
- EXPORT: controlled game-ready exports
- ADMIN: settings, integrations, permissions

Destructive operations require explicit approval. No automatic deletion.

## Job model
Long-running operations are jobs with: `job_id`, `asset_id`, `operation`, `pipeline`, `parameters`, `status`, `progress`, `result`, `errors`, `warnings`, `artifacts`, `audit_id`.

Statuses: QUEUED, RUNNING, WAITING, SUCCEEDED, FAILED, CANCELLED, BLOCKED, REQUIRES_APPROVAL.

## Validation gates
Geometry, UV, normals, materials, textures, LOD, collision, rig, animation, naming, transforms, and export compatibility.

Severity: INFO, WARNING, ERROR, BLOCKER.

A required BLOCKER prevents export/release.

## Evidence policy
MCP MUST distinguish specification readiness from runtime evidence. It MUST NOT claim Unreal build success, playtest success, or asset approval without corresponding evidence.

## Audit
Every mutation MUST produce an audit event containing actor, tool, asset, job, operation, permission, parameters hash, result, and timestamps. Secrets MUST never be logged.

## Definition of Done
v1.0 is complete when the server exposes stable schemas, read/analysis tools work, validation is evidence-backed, jobs are represented explicitly, permissions are enforced, audit records exist, and no unrestricted Blender execution is available. Build/export and WebMCP are subsequent controlled phases.
