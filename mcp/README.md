# NARIS MCP v0.1.0

Runnable read-only MCP orchestration server for CALL OF NARIS.

## Tools
- `naris_project_status`
- `naris_asset_validate`
- `naris_vertical_slice_status`
- `naris_qa_report`
- `naris_build_status`

## Local run

```bash
cd mcp
npm install
npm run build
NARIS_REPO=/path/to/naris npm start
```

MCP is the project/QA orchestration layer. Unreal Engine remains the production runtime. The server deliberately does not claim Unreal build or playtest success without evidence.
