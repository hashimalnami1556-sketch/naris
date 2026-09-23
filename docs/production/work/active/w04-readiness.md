---
status: active
last_updated: 2026-09-23
---
# W04 readiness handoff

- Task ID: NARIS-W04-READINESS
- Human decision owner: project owner.
- Executing agent: shared-agent integration pass.
- Claimed scope: static integration guards, Figma/Blender/Neon handoff, Windows runtime readiness.
- Goal: verify the checked-in W04 game on Windows and resolve remaining blockers.
- Completed prerequisite: shared KB routing, duplicate Unreal bootstrap cleanup, static integrity validation, world-generator edge-case repairs.
- Completed integration work: live Figma handoff file created; Blender validation/export helper added; Neon core schema contract added; repository validator extended to guard all three integration surfaces.
- Completed Blender bridge work: registry-gated Blender export, exchange schema, Unreal 5.4 Python importer, and Windows Blender-to-Unreal smoke-test script are checked in.
- Static validation evidence: GitHub Actions run 35855364699 passed MCP TypeScript build, Unreal project integrity, repository validation, and PowerShell bridge parsing.
- Source progression completed in this pass: interaction; checkpoint ID/location + respawn; Corrupted Heart step progression; Memory Crystal/FirstWhisper; Ash Gate; Celestial Wolf five modes + animation-driven attack impact; arena auto-start/lock; autonomous Bone Beast phase attacks; DemoEnd; native HUD with localized quest objective; automatic save recovery.
- Combat production readiness: hero TakeDamage routes through defense resolution; Parry rewards only resolved parries; Dodge has timed invulnerability; five-Essence cycling and Pause are input-bound; Hero, Wolf and Bone Beast expose animation-owned impact timing with smoke-only immediate fallbacks.
- Presentation binding readiness: 35 required VFX/AUD/Camera assets have registry identities and deterministic expected Unreal object paths. Current real bindings: 0/35. Shipping RC is intentionally blocked until every required payload resolves.
- Unreal Python bridge prerequisites enabled: PythonScriptPlugin + EditorScriptingUtilities.
- Windows packaging readiness: Development authoring/package/runtime smoke and bilingual profiling path is scripted; a separate Shipping RC path sets NARIS_PRESENTATION_STRICT=1 and rejects unbound presentation payloads before Shipping BuildCookRun. Neither path has executed on Windows in this session.
- CI evidence: NARIS CI run 35881766941 success; Content Validation run 35881766955 success; Unreal Validate run 35881766939 success for the checkpoint/quest integration baseline; subsequent changes remain guarded by the same tests. Manual Windows execution remains unperformed.
- Confirmed constraint: Unreal descriptor currently selects 5.4; Windows PC remains primary.
- Runtime blocker: registered AsusRog remote host is offline, so neither Blender nor Unreal can be executed from this session yet.
- Backend blocker: Neon connector requires a concrete project ID and the repository has no bound .neon/neon.json project metadata; no migration was applied.
- Open issues: Windows compile/package/runtime evidence; generated map/editor-load verification; 35 real Presentation asset bindings; production-authored meshes/animations/Niagara/audio/camera assets; Blender-to-Unreal real asset import; Arabic visual/RTL QA; measured performance; strict Shipping RC evidence.
- Missing sources: 18 attachment paths announced for this session were absent; no asset contents were inspected.
- Next action: when the Windows host/self-hosted runner is online, manually dispatch the full build/bootstrap/package/EN-AR launch-smoke workflow, retain logs/artifacts, then execute Blender-Unreal smoke and the W04 playtest from WakeArea through DemoEnd.
- Acceptance: a passing static check alone cannot close engine, DCC import, backend deployment or gameplay gates.
