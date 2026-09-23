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
- Confirmed constraint: Unreal descriptor currently selects 5.4; Windows PC remains primary.
- Runtime blocker: registered AsusRog remote host is offline, so neither Blender nor Unreal can be executed from this session yet.
- Backend blocker: Neon connector requires a concrete project ID and the repository has no bound .neon/neon.json project metadata; no migration was applied.
- Open issues: engine compile, authored map and binary assets, Blender-to-Unreal asset smoke test, full gameplay loop, save/load, performance and packaging remain unverified here. See the [gap register](../../../PROJECT_GAP_REGISTER.md).
- Missing sources: 18 attachment paths announced for this session were absent; no asset contents were inspected.
- Next action: bring the Windows host/self-hosted runner online, then invoke the existing manual Unreal build job with UNREAL_ENGINE_ROOT configured. On a passing build, run Blender export/import smoke tests and continue to editor playtest.
- Acceptance: a passing static check alone cannot close engine, DCC import, backend deployment or gameplay gates.
