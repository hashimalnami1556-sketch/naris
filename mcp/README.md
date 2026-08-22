# NARIS MCP

MCP orchestration layer for CALL OF NARIS.

## Architecture

`ChatGPT / MCP Client -> NARIS MCP -> GitHub / project files / QA metadata -> Unreal production runtime`

## First tool surface

The initial implementation contract is defined in `mcp/SPEC.md`.

### Read-only tools

- `naris_project_status` — repository and milestone status
- `naris_asset_validate` — canonical Asset ID/name validation
- `naris_vertical_slice_status` — W04 Ashen Forest progression gates
- `naris_qa_report` — evidence-backed QA checklist/report
- `naris_build_status` — build/release gate status

## Production rule

MCP is not the game engine. Unreal Engine remains the production runtime. MCP coordinates inspection, validation and controlled project operations.
