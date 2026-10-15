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
- Static validation: awaiting CI results on pull request. Unreal build: NOT RUN. Local installation: NOT RUN. Packaged game launch: NOT RUN.
- Blocker: Desktop Commander reports monthly usage quota exhausted, although AsusRog is paired online. Do not retry until quota resets.
- Blocker: canonical checkout may lack `.umap` gameplay level and the separately installed production module has a different source layout.
- Next action: complete CI, review merge, execute guarded Windows script on verified W04 project, capture the actual Unreal build and runtime screenshot/logs, then resolve remaining visual and AR/EN QA.
- Acceptance status: NOT ACCEPTED — native code authored but not compiled, installed, played, or approved.
