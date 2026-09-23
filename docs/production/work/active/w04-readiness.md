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
- Source progression completed in this pass: interaction dispatch; Waystone save/checkpoint; Memory Crystal -> FirstWhisper; Ash Gate persistence; Celestial Wolf bond/follow/EchoLink; keyboard/mouse + Xbox-style input; lock-on melee damage; Bone Beast completion/quest/DemoEnd; native smoke HUD; automatic save recovery.
- Combat production readiness: hero TakeDamage routes through defense resolution; Parry rewards only resolved parries; Dodge has timed invulnerability; five-Essence cycling and Pause are input-bound; native AnimNotifyState/AnimNotify hooks own production hit timing while smoke mode reuses the same Open -> Commit -> Close path.
- Unreal Python bridge prerequisites enabled: PythonScriptPlugin + EditorScriptingUtilities.
- Windows packaging readiness: authoring bootstrap generates W04_Prototype + smoke boss data; package launcher compiles EN/AR localization, runs BuildCookRun, runs a packaged progression/save-load runtime smoke, performs bilingual launch smoke, and requests CSV/GPU/LLM captures. This is scripted readiness, not execution evidence.
- CI evidence: NARIS CI run 35865086464 success; Content Validation run 35865086371 success; Unreal Validate run 35865086330 success. Manual Windows execution remains unperformed.
- Confirmed constraint: Unreal descriptor currently selects 5.4; Windows PC remains primary.
- Runtime blocker: registered AsusRog remote host is offline, so neither Blender nor Unreal can be executed from this session yet.
- Backend blocker: Neon connector requires a concrete project ID and the repository has no bound .neon/neon.json project metadata; no migration was applied.
- Open issues: Windows engine compile; generated smoke map/editor load verification; production-authored binary assets; Blender-to-Unreal real asset import; end-to-end playtest; runtime save/restart/load; Arabic visual/RTL QA; measured performance; final package evidence.
- Missing sources: 18 attachment paths announced for this session were absent; no asset contents were inspected.
- Next action: when the Windows host/self-hosted runner is online, manually dispatch the full build/bootstrap/package/EN-AR launch-smoke workflow, retain logs/artifacts, then execute Blender-Unreal smoke and the W04 playtest from WakeArea through DemoEnd.
- Acceptance: a passing static check alone cannot close engine, DCC import, backend deployment or gameplay gates.
