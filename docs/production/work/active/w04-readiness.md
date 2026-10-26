---
status: active
last_updated: 2026-10-26
---
# W04 readiness handoff

- Task ID: NARIS-W04-READINESS
- Human decision owner: project owner.
- Executing agent: shared-agent integration pass.
- Claimed scope: static integration guards, Figma/Blender/Neon handoff, Windows runtime readiness.
- Goal: verify the checked-in W04 game on Windows and resolve remaining blockers.
- Completed prerequisite: shared KB routing, duplicate Unreal bootstrap cleanup, static integrity validation, world-generator edge-case repairs.
- Completed integration work: live Figma handoff file created; Blender validation/export helper added; Neon core schema contract added; repository validator extended to guard all three integration surfaces.
- Completed Blender bridge work: registry-gated Blender export, exchange schema, Unreal Python importer (5.7 repository baseline), Windows Blender-to-Unreal smoke-test script, and `NARIS_Blender_Master_Builder_v1_1.py` authoring scaffold are checked in. The builder covers deterministic collections, prototype core assets, hero rig/actions, sockets, LOD/collision helpers, validation, manifest generation and preview exports; v1.1 binds all seven W04 core assets to canonical registry IDs and Unreal object paths, authors Memory Crystal, records triangle/material evidence, consumes the W04 environment contract, and has a headless Windows launcher for deterministic build plus registry-gated export; execution on Blender/Windows is still unverified.
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
- Confirmed constraint: Checked-in Unreal descriptor selects 5.7; Windows PC remains primary. Historical 5.4 references are stale.
- Runtime blocker: remote execution is currently unavailable due to Desktop Commander usage limits; neither Blender nor Unreal has been executed in this session.
- Backend blocker: Neon connector requires a concrete project ID and the repository has no bound .neon/neon.json project metadata; no migration was applied.
- Open issues: Windows compile/package/runtime evidence; actual W04_AshenForest production map; seven core production meshes; approved surface/water master materials + generated instances; 16 Audio + 14 Niagara payloads; 10 production AnimMontages; real Blender-to-Unreal Factory v2 run; Arabic visual/RTL QA; measured hardware performance; strict Shipping RC evidence.
- Missing sources: 18 attachment paths announced for this session were absent; no asset contents were inspected.
- Next action: when Windows is online, run `tools/windows/Invoke-NarisBlenderMasterBuilder.ps1 -ExportCoreAssets` and retain its blend/validation/manifest/export evidence; then compile NARIS_W04Editor, run the W04 Environment Factory bridge and production blockout authoring, retain all reports, and execute Development package/runtime smoke before attempting the strict W04_AshenForest Shipping RC.
- Acceptance: a passing static check alone cannot close engine, DCC import, backend deployment or gameplay gates.

## 2026-10-22 next-execution handoff

1. Preserve and hash the local `Game/NARIS_UE57` project before any import; compare against `unreal/NARIS_W04` without overwriting local `.umap`/`.uasset` content.
2. Execute the repository CI and manually dispatch the Windows **development** package gate on a configured `[self-hosted, windows, unreal]` runner with `UNREAL_ENGINE_ROOT` pointing to UE 5.7.
3. Retain the `NARIS_W04-Windows-Diagnostics` artifact on failure and address the first failing build/authoring/asset validation step before rerunning.
4. Do not promote smoke-only W04_Prototype assets to shipping. Validate the production W04_AshenForest map, core meshes, animation montages, audio/Niagara and materials separately.
5. Gate release on packaged progression/save-load, EN/AR/RTL, fatal/crash logs and measured FPS evidence.

**Evidence status:** documentation handoff only. No workstation execution, Unreal compilation or Windows package test was performed during this update.

## 2026-10-26 Stage8 executing claim

- Executing agent: Codex (current session).
- Authorized scope: apply owner-approved canonical zones, fix Windows build entry point, harden map promotion and retained evidence, test and update main without replacing production assets.
- Owner instruction: implement and activate all currently canonical zones. This is design/implementation authorization; asset QA and release gates remain mandatory.
- Workstation check: AsusRog reported offline. Unreal and Windows package execution are not available in this session.
- Active changes: shipping wrapper, candidate-map validation and focused regression coverage.

### Stage8 source changes completed

- Replaced the invalid shipping commandlet call with canonical Development/Shipping routing and engine-version checks.
- Added isolated package directories, historical-report quarantine, executable hashes and explicit unresolved runtime approval fields.
- Added data-driven structural map checks and candidate preflight without renaming or removing actors.
- Recorded owner authorization for all canonical W04 zones; kept registry technical approvals unchanged.
- Verified 350 CI tests, 6 AssetForge tests and repository validation locally. PowerShell parsing is assigned to hosted CI because pwsh is not installed in this execution environment.
- Remaining blocker: authorized AsusRog device is offline; Windows Unreal build, production .umap, EXE and playtest are not produced here. The main-push Shipping workflow now exposes the engine phase on the configured self-hosted runner.
- Next action: retain hosted CI results and the self-hosted build status; when a Windows Unreal runner executes, address its first strict-gate failure and retain diagnostics rather than marking missing artifacts complete.
