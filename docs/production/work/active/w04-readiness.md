---
status: active
last_updated: 2026-10-11
---
# W04 readiness handoff

- Task ID: NARIS-W04-READINESS
- Human decision owner: project owner.
- Executing agent: shared-agent integration pass.
- Claimed scope: static integration guards, Figma/Blender/Neon handoff, Windows runtime readiness.
- Goal: verify the checked-in W04 game on Windows and resolve remaining blockers.
- Completed prerequisite: shared KB routing, duplicate Unreal bootstrap cleanup, static integrity validation, world-generator edge-case repairs.
- Completed integration work: live Figma handoff file created; Blender validation/export helper added; Neon core schema contract added; repository validator extended to guard all three integration surfaces.
- Completed Blender bridge work: registry-gated Blender export, exchange schema, Unreal 5.4 Python importer, Windows Blender-to-Unreal smoke-test script, and `NARIS_Blender_Master_Builder_v1_1.py` authoring scaffold are checked in. The builder covers deterministic collections, prototype core assets, hero rig/actions, sockets, LOD/collision helpers, validation, manifest generation and preview exports; v1.1 binds all seven W04 core assets to canonical registry IDs and Unreal object paths, authors Memory Crystal, records triangle/material evidence, consumes the W04 environment contract, and has a headless Windows launcher for deterministic build plus registry-gated export; execution on Blender/Windows is still unverified.
- Static validation evidence: GitHub Actions run 35855364699 passed MCP TypeScript build, Unreal project integrity, repository validation, and PowerShell bridge parsing.
- Source progression completed in this pass: interaction; checkpoint ID/location + respawn; Corrupted Heart step progression; Memory Crystal/FirstWhisper; Ash Gate; Celestial Wolf five modes + animation-driven attack impact; arena auto-start/lock; autonomous Bone Beast phase attacks; DemoEnd; native HUD with localized quest objective; automatic save recovery.
- Combat production readiness: hero TakeDamage routes through defense resolution; Parry rewards only resolved parries; Dodge has timed invulnerability; five-Essence cycling and Pause are input-bound; Hero, Wolf and Bone Beast expose animation-owned impact timing with smoke-only immediate fallbacks.
- Front-end/settings/controls readiness: native front-end, pause, settings and controller-remap pages exist; 11 gameplay actions can be remapped with conflict/reserved-key protection and persisted InputSettings. NarisGameUserSettings drives graphics/audio/accessibility with EN/AR strings; presentation sound routing now supports explicit SFX/Music/Voice buses.
- Subtitle readiness: NarisSubtitleSubsystem + HUD rendering respect enabled/scale settings and accept authored Memory Crystal dialogue; no fabricated default First Whisper dialogue is embedded in C++.
- Animation readiness: 10 registry-backed production AnimMontages have deterministic targets. Development authoring reports missing assets; strict Shipping validates montage type, required impact notifies and positive Hero hit-window duration.
- Core asset readiness: seven W04 core art assets are registry-backed with deterministic Unreal paths and technical validation for materials/LODs, skeletal Skeleton+PhysicsAsset, static collision, Nanite state/triangle evidence and documented material/triangle budgets.
- Material readiness: ten W04 MaterialInstance targets map directly to the authored Ashen Forest library. Master parameter/blend capability is validated; instance authoring is deterministic once approved surface/water masters exist. Shipping rejects missing masters/instances or PBR drift.
- World/environment readiness: LEVEL_LAYOUT drives six production zones; W04_AshenForest_Blockout authoring is scripted and explicitly non-shippable. Shipping validates W04_AshenForest only. Factory v2 is the runtime environment-config authority and has an end-to-end Blender .blend -> FBX/GLB/manifest -> Unreal import launcher.
- Presentation binding readiness: all 35 VFX/AUD/Camera assets have registry identities and deterministic targets. Five native C++ CameraShake classes are bound; 30 payloads remain unresolved (16 Audio, 14 Niagara VFX). Shipping RC remains intentionally blocked until all required payloads resolve and validate.
- Unreal Python bridge prerequisites enabled: PythonScriptPlugin + EditorScriptingUtilities.
- Presentation source intake: 16 deterministic WAV source slots + SFX generation contracts exist; WAV import validates PCM 48 kHz/24-bit, channels, duration, digital silence and -1 dBFS peak ceiling. Niagara binding/profile authoring rejects systems with zero emitter handles.
- Windows packaging readiness: Development authoring/package/runtime smoke, material/core-asset/animation reports, fatal-log/crash QA and bilingual CSV/GPU/LLM profiling are scripted. Shipping RC enforces strict animation/core-asset/material/presentation gates plus the production Ashen Forest map before Shipping BuildCookRun. Neither Windows path has executed in this session.
- CI evidence: NARIS CI run 35904765067 success; Content Validation run 35904765117 success; Unreal Validate run 35904765189 success. Manual Windows execution remains unperformed.
- Confirmed constraint: Unreal descriptor currently selects 5.4; Windows PC remains primary.
- Runtime blocker: registered AsusRog remote host is offline, so neither Blender nor Unreal can be executed from this session yet.
- Backend blocker: Neon connector requires a concrete project ID and the repository has no bound .neon/neon.json project metadata; no migration was applied.
- Open issues: Windows compile/package/runtime evidence; actual W04_AshenForest production map; seven core production meshes; approved surface/water master materials + generated instances; 16 Audio + 14 Niagara payloads; 10 production AnimMontages; real Blender-to-Unreal Factory v2 run; Arabic visual/RTL QA; measured hardware performance; strict Shipping RC evidence.
- Missing sources: 18 attachment paths announced for this session were absent; no asset contents were inspected.
- Next action: when Windows is online, run `tools/windows/Invoke-NarisBlenderMasterBuilder.ps1 -ExportCoreAssets` and retain its blend/validation/manifest/export evidence; then compile NARIS_W04Editor, run the W04 Environment Factory bridge and production blockout authoring, retain all reports, and execute Development package/runtime smoke before attempting the strict W04_AshenForest Shipping RC.
- Acceptance: a passing static check alone cannot close engine, DCC import, backend deployment or gameplay gates.

## 2026-10-11 repository input repair

- Executing agent: Codex.
- Claimed scope: hero keyboard jump, menu input routing, static regression checks.
- Baseline: main at 47b67de; this checkout predates uncommitted workstation changes. Do not overwrite the live Windows checkout with these files without reviewing its diff.
- Remote Desktop execution is paused by the monthly tool quota. Unreal and Blender execution are unavailable in this environment.
- Inspection: repository hero has no Jump bindings; Space is mapped to Dodge. Controller menu bindings consume shared keyboard/gamepad keys even when their handlers return because menus are closed.
- Work in progress: repair keyboard jump and menu consumption without changing skeletons or production asset approval.

- Completed: Jump press/release bindings; Space for Jump and LeftControl for keyboard Dodge; JumpZVelocity 600, AirControl 0.8, GravityScale 1.5 defaults. Existing Blueprint overrides and saved mappings still need inspection on the workstation. Gamepad Dodge is preserved; gamepad Jump is not added in this scoped repair.
- Completed: menu navigation only consumes input while a system menu is open; setup handles an already-open menu, and each open/close updates bindings. Bypass launches explicitly select GameOnly input.
- Completed: repaired pre-existing EN/AR PO source drift for PauseMenuHint and SettingsMenuHint, including the mouse-click translation. Updated the stale controller contract assertion to the already checked-in FInputKeyEventArgs signature.
- Verification: repository validation passes; Unreal source integrity passes; 6 AssetForge tests pass. Full CI contract suite passes after the stale assertion repair (301 tests). These checks inspect source/data; they do not execute Unreal.
- Workstation merge gate: review remote uncommitted changes first, compile with UE 5.7, then verify normal front-end, New/Continue, W/A/S/D, Space press/release and landing, LeftControl dodge, repeated pause/resume with Escape, shared gamepad menu actions and swimming ascent/descent. Confirm menu input does not trigger gameplay and controls resume after closing. Retain logs and save hashes.
- Blockers: no UE/Blender binaries or production assets in this checkout; remote tool quota paused. Final wolf appearance/rig/animation, foot sliding and Shipping readiness remain unverified. Do not promote the V10 candidate or change skeleton retargeting based on this input repair.
- Next action: review this isolated source diff alongside the live Windows checkout, then run the engine gate above before integration.

### Companion follow-up — 2026-10-11

- Executing agent: Codex. Scope: cancel stale wolf attack requests and correct ground-follow distance/direction.
- Mode changes now clear the pending attack target; impact notifies reject an unbonded wolf or a wolf outside Attack mode. This prevents a delayed bite from applying damage after a Follow/Guard/Track/EchoLink command.
- Ground movement now uses horizontal distance and direction. A vertical offset alone no longer causes a standing wolf to keep requesting movement or attenuates its horizontal input. This is not NavMesh/pathfinding or foot IK implementation.
- Remote publication attempt was rejected by automatic approval review despite a brief user approval; no publication is claimed. Explicit approval naming payload and public destination remains required.
- Engine regression gate: request an animation-driven bite, change to Follow before impact, verify zero damage, then verify an uninterrupted Attack bite damages once. Test same-XY/different-height follow and normal horizontal follow separately.
- Final wolf mesh production remains blocked by remote execution quota; no asset approval is inferred from these source changes.

- Follow-up verification: repository validator, Unreal source integrity and all 301 CI source/data tests pass locally. No engine compile or PIE test was performed.
