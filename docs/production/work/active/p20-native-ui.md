---
status: active
last_updated: 2026-10-15
---
# P20 native UI installation and runtime handoff

- Task ID: NARIS-W04-P20-UI
- Human decision owner: project owner (requested installation and running the new interface).
- Executing agent: ChatGPT P20 integration pass, 2026-10-15.
- Scope claimed: W04 combat HUD presentation, UMG cinematic main menu, native source contracts and safe Windows build/launch helper. No edits to the separate on-device `NARIS_UE57` project.
- Completed: translated the P20 browser visual hierarchy into native W04 combat HUD backed by live combat/energy/boss components; compact translucent front-end and fully opaque submenu treatment; kept input remapping, gameplay, save state and boss identity.
- Completed: source-level regression tests, README/runbook and build/launch preflight script.
- Static validation: PASS (NARIS CI, NARIS Unreal Validate, NARIS Content Validation and NARIS Codex PR Check on candidate SHA ce0ccef). Unreal build: NOT RUN. Local installation: NOT RUN. Packaged game launch: NOT RUN.
- Blocker: Desktop Commander reports monthly usage quota exhausted, although AsusRog is paired online. Do not retry until quota resets.
- Blocker: canonical checkout may lack `.umap` gameplay level and the separately installed production module has a different source layout.
- Next action: self-hosted Windows verification is QUEUED (GitHub Actions run 38802930780, no runner assigned at handoff); once a runner is available, review its build evidence before any merge. Actual interactive game launch, screenshots and gameplay QA still require a verified installed W04 level.
- Acceptance status: NOT ACCEPTED — native code authored but not compiled, installed, played, or approved.
