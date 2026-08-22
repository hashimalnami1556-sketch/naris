# NARIS MCP — SPEC

## Purpose
Provide a controlled MCP interface for the CALL OF NARIS production repository. The MCP layer orchestrates project inspection, asset validation, build/QA metadata, and production status. It does not replace Unreal Engine as the production runtime.

## Scope
- Project status and milestone inspection
- Asset manifest and naming validation
- W04 Ashen Forest vertical-slice validation
- QA checklist generation/reporting
- Build metadata and release gates
- Read-only diagnostics first; write operations require explicit tool contracts

## Runtime boundary
Unreal Engine is the production game runtime. MCP is the orchestration and project-operations layer.

## Canonical asset ID
`NARIS-W<world>-<domain>-<type>-<sequence>`

## Initial tools
- `naris_project_status`
- `naris_asset_validate`
- `naris_vertical_slice_status`
- `naris_qa_report`
- `naris_build_status`

## Safety
- Never delete assets automatically.
- Never overwrite immutable Asset IDs.
- Never claim a build/playtest passed without evidence.
- Prefer read-only inspection before mutation.

## Definition of Done
The MCP layer is useful when an assistant can inspect the repository, validate W04, identify missing production gates, and produce evidence-backed status without inventing completion.
