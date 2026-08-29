# NARIS MCP Server

Initial v1.0 scaffold.

## Planned modules
- `src/server.ts` — MCP server bootstrap and transport.
- `src/tools/` — governed MCP tool registrations.
- `src/permissions/` — least-privilege authorization.
- `src/audit/` — immutable operation audit records.
- `src/transport/` — transport adapters.

Business logic must live in shared packages, not inside individual MCP handlers, so WebMCP can later bridge the same contracts.

## First implementation slice
1. project status
2. asset list/search/get
3. asset inspect
4. validation run/report
5. job status

Build/export tools follow after the read/analyze surface is verified.
