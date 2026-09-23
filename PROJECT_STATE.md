# NARIS current work

Updated: 2026-09-23

- Objective: maintain a shared, evidence-based project KB and unblock the Windows W04 vertical slice.
- Human decision owner: project owner (repository user).
- Executing agent: shared-agent integration pass active for Figma/Blender/Neon and W04 readiness.
- Current work: [W04 follow-up](docs/production/work/active/w04-readiness.md).
- Source routing: [knowledge sources](docs/production/knowledge-sources.md).
- Production readiness: [production status](docs/PRODUCTION_STATUS.md).
- Work navigation: [work index](docs/production/work/index.md).
- Integration contract: [Figma, Blender and Neon](docs/production/INTEGRATIONS_FIGMA_BLENDER_NEON.md).
- Figma: live file created and structured at https://www.figma.com/design/lYSmWwGHXCEXODKpG9bpJH.
- Blender: deterministic validation/export helper is checked in; runtime execution is pending because the registered AsusRog host is offline.
- Neon: core PostgreSQL schema contract is checked in; no remote project/branch is bound yet, so no migration has been applied.
- Next action: when the Windows runner/AsusRog host is online, run NARIS_W04Editor build with Unreal 5.4, retain the log, then run Blender export/import smoke tests and editor asset validation.
- Blockers: registered AsusRog remote host is offline; no bound Neon project ID; no Claude Code session available here; the 18 announced attachment paths were absent. No Unreal engine build or playtest has been executed in this pass.

Do not treat static validation, Figma design, Blender source/export contracts or Neon schema files as engine/runtime evidence. The checked-in Unreal descriptor selects 5.4; changing that baseline needs an explicit migration and build evidence.
