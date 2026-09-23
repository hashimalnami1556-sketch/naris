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
- Source progression completed in this pass: E-key interaction dispatch via INarisInteractable; persistent Waystone checkpoint/autosave; Memory Crystal -> First Whisper narrative save state; Ash Gate unlock prerequisite, blocker disable, autosave and reload restoration.
- Unreal Python bridge prerequisites enabled: PythonScriptPlugin + EditorScriptingUtilities.
- CI evidence: run 35858817921 NARIS CI success; run 35858818007 Content Validation success; run 35858817934 Unreal Validate success.
- Confirmed constraint: Unreal descriptor currently selects 5.4; Windows PC remains primary.
- Runtime blocker: registered AsusRog remote host is offline, so neither Blender nor Unreal can be executed from this session yet.
- Backend blocker: Neon connector requires a concrete project ID and the repository has no bound .neon/neon.json project metadata; no migration was applied.
- Open issues: engine compile, authored map and binary assets, Blender-to-Unreal asset smoke test, full gameplay loop, save/load, performance and packaging remain unverified here. See the [gap register](../../../PROJECT_GAP_REGISTER.md).
- Missing sources: 18 attachment paths announced for this session were absent; no asset contents were inspected.
- Next action: implement Celestial Wolf progression/companion contract in source; when the Windows host is online, run NARIS_W04Editor build and the Blender-Unreal smoke command against a real registered .blend asset.
- Acceptance: a passing static check alone cannot close engine, DCC import, backend deployment or gameplay gates.
