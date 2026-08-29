# NARIS MCP v1.0 Specification

## Purpose
NARIS MCP is the agent-facing control layer for CALL OF NARIS production. It exposes governed project, asset, build, validation, export, job, and reporting operations without exposing arbitrary Blender execution.

## Architecture
AI/ChatGPT → NARIS MCP Server → governed job layer → NARIS Blender Worker → Blender / Asset Store.

WebMCP is a browser-facing compatibility layer and must reuse these contracts rather than duplicate business logic.

## Canonical principles
- GitHub remains the versioned source of truth for specifications, schemas, pipeline definitions, automation and release history.
- Every production asset has one immutable NARIS Asset ID.
- Asset lifecycle: Concept → Design → Asset ID → Source Art → Registry → Unreal Import → Integration → QA → Approved → Release.
- MCP tools are least-privilege and auditable.
- Arbitrary Blender Python execution is out of scope for v1.0.
- Write/destructive operations require explicit tool parameters and permission checks.

## v1.0 tools
### Read
- `naris.project.status`
- `naris.project.get_settings`
- `naris.asset.list`
- `naris.asset.search`
- `naris.asset.get`
- `naris.asset.inspect`
- `naris.job.status`
- `naris.validation.get_report`

### Analyze
- `naris.project.validate`
- `naris.validation.run`
- `naris.validation.list_failures`
- `naris.report.generate`

### Build / Write
- `naris.asset.build`
- `naris.asset.export`

## Tool contract
Every tool defines: name, title, description, input schema, output schema, annotations, permission, audit policy, and side-effect classification.

## Permissions
- `project.read`
- `asset.read`
- `validation.run`
- `build.execute`
- `export.execute`
- `report.generate`
- `project.admin`

## Asset inspection
Inspection should cover geometry, transforms, normals, UV, materials, textures, LOD, collision, rig, animation, naming, scale and export compatibility.

## Validation states
`PASS`, `WARNING`, `ERROR`, `BLOCKED`.

## Job model
Long-running operations return a job identifier. Jobs expose status, progress, result, errors and timestamps. Supported operation classes include BUILD_ASSET, VALIDATE_ASSET, GENERATE_LOD, GENERATE_COLLISION, BAKE_TEXTURES, EXPORT_ASSET and RENDER_PREVIEW.

## Export profiles
Initial formats: GLB, GLTF, FBX, OBJ. Export may be blocked when required validation gates fail.

## Audit
Every write/build/export operation records actor, tool, asset ID, parameters summary, start/end time, status and resulting artifact/job ID. Secrets and unnecessary PII must never be returned.

## v1.0 out of scope
- Arbitrary Blender Python execution
- Autonomous destructive deletion
- Direct database administration
- Production credential management inside tool payloads
- Full Unreal/Unity/Godot automation

## Compatibility
Designed for a TypeScript MCP server, a Python Blender worker, and a future WebMCP bridge. Schemas should remain transport-neutral.
