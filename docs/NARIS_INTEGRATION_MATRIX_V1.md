# NARIS Integration Matrix v1

## Canonical flow
AI Agent → NARIS MCP → Permission Gate → Asset Registry → Job Queue → Blender Worker → NARIS Toolkit → Validation → Artifact → Export → Report → Audit.

## Integrations

| System | Role | Contract | Authority |
|---|---|---|---|
| Blender 4.x | Asset creation/inspection | named worker operations | NARIS Toolkit |
| GitHub | source of truth | repo/docs/schemas/CI | repository |
| WebMCP | browser-facing discovery/actions | governed tool facade | NARIS MCP |
| MCP App | operator UI | project/assets/jobs/validation/export views | NARIS MCP |
| Figma | product/UI design | screens, components, design tokens | design source |
| Product Design | UX/product flow | briefs, audits, prototypes | product source |
| Gamma/Canva | presentation | stakeholder deck | communication layer |
| Magnific/Image generation | visual exploration | concept/key-art references | creative source |
| ROGNALIA note Studio mini | notes/knowledge handoff | notes → structured project context | optional adapter |

## Security boundary
- Never place API keys, tokens, passwords, private keys, or secrets in repository specs.
- AI receives named operations and validated schemas, never arbitrary Blender Python.
- WebMCP cannot bypass MCP permissions.
- Generated artifacts must remain distinguishable from source assets.
- Runtime success must be backed by worker evidence; documentation alone is not execution evidence.

## v1 readiness
- MCP specification: present.
- Tool contract schema: present.
- Job queue primitives: present.
- Permission primitives: present.
- Blender Worker adapter: boundary present; transport still requires implementation.
- WebMCP: contract/design stage.
- MCP App: product/design stage.
- External creative-tool adapters: role definitions only until their authenticated APIs/connectors are configured.
