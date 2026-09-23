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
- Blender: deterministic validation/export helper is checked in and the export path is gated by the canonical asset registry; runtime execution is still pending because the registered AsusRog host is offline.
- Blender -> Unreal bridge: exchange schema, Unreal Python importer, and Windows smoke-test script are checked in.
- W04 source progression now covers interaction, Waystone checkpoint/autosave, Memory Crystal -> FirstWhisper, Ash Gate persistence, Celestial Wolf bond/follow/EchoLink, lock-on melee damage, Bone Beast defeat, quest completion and DemoEnd persistence.
- Combat production pass adds real incoming-hit defense routing, timed Parry/Dodge windows, five-Essence cycling, pause/resume input, and native animation hit-window/impact notifies with a smoke-only immediate fallback.
- A packaged runtime smoke director now drives Waystone -> Memory Crystal -> Ash Gate -> Celestial Wolf -> Bone Beast -> DemoEnd and performs an isolated Save -> New Game -> Load round-trip before bilingual launch smoke.
- Unreal editor scripting prerequisites are enabled in the .uproject: PythonScriptPlugin and EditorScriptingUtilities.
- Windows authoring bootstrap can generate the smoke W04_Prototype.umap and DA_BoneBeast_Smoke.uasset after a successful editor build; these binaries are not currently committed evidence.
- Windows package pipeline: Build Editor -> generate smoke assets -> compile EN/AR localization -> BuildCookRun Win64 Development -> launch EN and AR smoke -> CSV/GPU/LLM profiling -> package artifact/report.
- Verified CI evidence: NARIS CI run 35865086464 success; Content Validation run 35865086371 success; Unreal Validate run 35865086330 success. The manual self-hosted Windows package/runtime smoke job remains skipped on normal pushes.
- Static evidence: NARIS CI run 35855364699 passed MCP TypeScript build, Unreal project integrity, repository validation and PowerShell bridge parsing.
- Neon: core PostgreSQL schema contract is checked in; no remote project/branch is bound yet, so no migration has been applied.
- Next action: bring the Windows self-hosted runner/AsusRog online and manually dispatch the full Unreal build/bootstrap/package/runtime-smoke/EN-AR launch/profiling gate; then run Blender->Unreal real-asset smoke and the editor playtest.
- Blockers: registered AsusRog remote host is offline; no Windows UnrealBuildTool/package/playtest evidence yet; no bound Neon project ID; no Claude Code session available here; the 18 announced attachment paths were absent.

Do not treat static validation, Figma design, Blender source/export contracts or Neon schema files as engine/runtime evidence. The checked-in Unreal descriptor selects 5.4; changing that baseline needs an explicit migration and build evidence.
