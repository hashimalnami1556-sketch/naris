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

### Map UI follow-up — 2026-10-11

- Executing agent: Codex. Claimed scope: HUD map projection and content-page confirmation routing. Existing map artwork consists of two fixed lines and does not consume world positions.
- Implement a player-centered schematic with actual discovered waystone positions and a heading marker. This does not create terrain artwork, production map assets or fast travel. Engine validation remains blocked by remote quota.
- Completed: square, altitude-independent world projection (+X up, +Y right), player heading, discovered loaded waystone markers filtered by MapId, border-safe marker culling, editable 100 m default world radius and EN/AR schematic heading. Unloaded actors and destinations outside the local radius are not shown; the discovered list remains available.
- Completed: MenuConfirm only dispatches settings actions on the Settings page. Inventory/Map/Quests no longer fall through to settings using a stale menu index.
- Verification: repository/localization validator, Unreal source validator, all 301 CI tests and 6 AssetForge tests pass; diff whitespace check passes. Added NARIS.UI.Map.Projection engine automation coverage for axes, centering, altitude, marker borders and zero radius; it cannot run without Unreal.
- Refreshed origin/main to ef013ed; its Windows launcher/UI4.1 changes do not overlap this scope and were not overwritten.
- Engine gate: compile UE 5.7; test the map with a possessed hero, rotate/move/reopen, discover two waystones at known XY offsets, verify undiscovered/off-range/other-MapId markers absent and verify Confirm on content pages leaves settings unchanged. Verify Arabic rendering separately. No final executable or production asset readiness is claimed.

### Packaged launch follow-up — 2026-10-11

- Executing agent: Codex. Claimed scope: Start-NarisGame.ps1 and launch recovery documentation. Refreshed the working branch onto origin/main ef013ed; retained all input/map/companion changes.
- Inspection: launcher defaults to C:\Users\Admin\NARIS instead of the known canonical checkout, misses nested W04 staged packages and directly packaged Win64 executable names, and accepts unrelated recently started game processes as bootstrap children.
- Completed: canonical default path, nested W04 staged packages, launcher-checkout discovery and direct Win64 Development/Shipping executable names. Bootstrap checks now require a newly created direct child whose executable lies inside the selected package directory. Existing editors, saves and builds are untouched.
- Verification: repository validator and all 306 CI source/data tests plus 6 AssetForge tests pass on the refreshed checkout; diff whitespace check passes. PowerShell/Windows and Unreal are unavailable here, so execution and packaged runtime acceptance remain pending.
- Next gate: run -ListOnly on Windows, choose the intended package explicitly if multiple candidates exist, test both a root bootstrap and direct Win64 executable, and verify unrelated running game instances cannot satisfy a failed launch. A modification timestamp does not prove the newest approved release.

### Uploaded asset production intake — 2026-10-11

- Executing agent: Codex. Claimed scope: five uploaded GLBs, USD extension repair, geometry validation, isolated Unreal review importer and exact ComfyUI generation preparation. Details: [uploaded candidate record](../../uploaded-candidates-20261011.md).
- Actual bytes inspected: four static GLBs; one rigged GLB with 18 joints and one single-channel Idle rotation animation. Registered new W04 INTAKE blockout IDs without replacing core production bindings. Container/accessor/index/weight checks pass on all five files.
- Corrected the uploaded USDC crate's `.usdz` extension in a separate preserved-byte copy. Did not claim ZIP conversion or USD engine import.
- Added an editor authoring path and guarded Windows build/import/review launcher. Geometry previews are local source renders, not engine evidence.
- Preserved requested 40 steps, CFG 7.5, DPM++ 2M Karras, 1344x768 in six ComfyUI API workflows plus a queue runner. Live fal SDXL schema lacks sampler selection; no incompatible generation was submitted. Generation remains not_run.
- Rechecked remote device: AsusRog is Offline. No Unreal/Blender build, import, PIE, game launch or final packaging was performed in this environment.
- Next action: run the review launcher on Windows, retain the editor report/logs and inspect materials/scale, then validate reference fidelity, production rigs and authored navigation before promotion. Main/default maps and production art remain unchanged.
- Verification: repository validator passes; 312 CI tests (including six byte-level intake tests) and six AssetForge tests pass, 318 total. Python sources parse; diff whitespace check passes. Windows launcher and Unreal importer remain unexecuted.


### Generation receipt recovery — 2026-10-12

- Executing agent: Codex. Scope: generation queue receipts, resumed submissions and regression tests. Baseline: published intake commit 8ea68cd. The prior intake's 24 files were verified byte-identical to the local delivery tree.
- Found: rerunning the six-job runner overwrote previous receipts and submitted accepted jobs again. Fixed: retain receipts, identify exact workflows, skip accepted jobs (including legacy receipts), checkpoint submission intent before POST, save atomically and prevent concurrent runners with a journal lock.
- Ambiguous network failures and rejected submissions remain explicit unresolved records; no automatic resubmission is allowed. Check the server history and repair the receipt only after determining whether a prompt was accepted. A crash may leave a lock; remove it only after verifying no runner is active.
- No settings, prompts, seeds, geometry, production-map bindings or approval states changed. AsusRog was rechecked and remains Offline; no new images, Unreal import, PIE or final package were executed.
- Verification: repository validation and 318 CI tests plus six AssetForge tests pass (324 total). Six new receipt tests cover repeat invocation, network uncertainty, legacy receipts, invalid journals, concurrent runners and rejected workflows. These tests use a simulated submit transport, not a live generation service.
