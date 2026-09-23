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
- W04 source progression now covers interaction; Waystone checkpoint ID/location + respawn; Memory Crystal -> FirstWhisper; Corrupted Heart quest steps 1-4; Ash Gate persistence; Celestial Wolf bond/modes/animation-driven attacks; arena auto-entry; Bone Beast autonomous phase attacks; quest completion; DemoEnd persistence; and localized HUD objectives.
- Combat production pass adds real incoming-hit defense routing, timed Parry/Dodge windows, five-Essence cycling, pause/resume input, and native animation hit-window/impact notifies with a smoke-only immediate fallback.
- A packaged runtime smoke director now drives Waystone -> Memory Crystal -> Ash Gate -> Celestial Wolf -> Bone Beast -> DemoEnd, verifies Corrupted Heart steps and checkpoint location, then performs an isolated Save -> New Game -> Load round-trip before bilingual launch smoke.
- Presentation readiness: shared cue bus/profile authoring exists; 35/35 required VFX/AUD/Camera IDs are registered and have deterministic expected Unreal object paths, but 0/35 are currently bound to real Unreal assets. Development smoke permits explicit unbound payloads; Shipping RC rejects them.
- Unreal editor scripting prerequisites are enabled in the .uproject: PythonScriptPlugin and EditorScriptingUtilities.
- Windows authoring bootstrap can generate the smoke W04_Prototype.umap and DA_BoneBeast_Smoke.uasset after a successful editor build; these binaries are not currently committed evidence.
- Windows package pipeline: Development = build editor -> author smoke map/boss/presentation profile -> compile EN/AR -> BuildCookRun -> packaged progression/save-load smoke -> EN/AR launch -> CSV/GPU/LLM capture. Shipping RC = strict presentation bindings -> Shipping BuildCookRun -> artifact/report.
- Verified CI evidence: NARIS CI run 35881766941 success; Content Validation run 35881766955 success; Unreal Validate run 35881766939 success. Later source commits continue through the same guarded workflow; Windows self-hosted execution remains manual.
- Static evidence: NARIS CI run 35855364699 passed MCP TypeScript build, Unreal project integrity, repository validation and PowerShell bridge parsing.
- Neon: core PostgreSQL schema contract is checked in; no remote project/branch is bound yet, so no migration has been applied.
- Next action: bind/import the 35 real Presentation assets at their deterministic Unreal target paths and bring AsusRog/self-hosted Windows online to run Development package/runtime smoke, Blender->Unreal asset import, editor playtest, and then strict Shipping RC.
- Blockers: registered AsusRog remote host is offline; no Windows UnrealBuildTool/package/playtest evidence yet; no bound Neon project ID; no Claude Code session available here; the 18 announced attachment paths were absent.

Do not treat static validation, Figma design, Blender source/export contracts or Neon schema files as engine/runtime evidence. The checked-in Unreal descriptor selects 5.4; changing that baseline needs an explicit migration and build evidence.
