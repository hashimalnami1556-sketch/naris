---
status: active
last_updated: 2026-10-18
---
# W04 readiness handoff

## 2026-10-18 stale input repair claim

- Executing agent: Codex. Scope: fail-closed movement sample lifetime, controller ownership, paused/ignored input and release handling; preserve the freshly synchronized smooth-control implementation.
- Starting revision: `afb3792c164d50490bf669ca1eba1fa1b15da481`. AsusRog is offline at this check (last seen 47 hours ago).
- Native Unreal compilation and runtime acceptance remain open. No original source asset or canonical W04 actor is to be replaced.
- Completed: real-time sample lease, Controller-scoped reset, paused/ignored input guards, ignored-look lock yaw guard and zero/invalid-delta release correction. One real shared-filter regression failed before repair; 195 portable/mocked tests now pass (104 compiled C++ cases).
- Next: compile UE 5.7 and execute timeout/pause/focus/possession rows in the engine acceptance matrix. Preserve explicit reset events; the lease is a fallback, not a focus detector.

## 2026-10-17 smooth-control repository integration

- Executing agent: Codex. Scope: reconcile the completed P15 control source delivery with PR #46; run repository checks and retain engine acceptance as a separate gate.
- Starting revision: `3b488e00c65327b0a0535db3fcffee97c3f615e7`, freshly inspected. The prior source-inclusive delivery matches every overlapping repository file except its intentionally repository-scoped manifest.
- Claimed paths: `source/p15-combat/`, `PROJECT_STATE.md`, this work record and `docs/PRODUCTION_STATUS.md`. Preserve canonical W04 actor/input/health ownership, registry approvals and original asset bytes.
- Live host check: AsusRog offline, last seen 37 hours ago. No local Unreal installation is available. No UHT/UBT, project installation, animation graph authoring or gameplay result is claimed.
- Completed: integrated the prior delivery into `source/p15-combat/`, retained repository-scoped manifests and external asset provenance, and updated current-state/acceptance documentation. Native additions cover baseline movement, bounded lock heading, camera modes, replicated action/hit/recovery phase, cancel notifies and locomotion data.
- Fresh validation: 184 P15 tests (93 compiled portable C++ cases), 336 repository contracts, 6 AssetForge tests and repository validation passed; see `source/p15-combat/Reports/repository_checks.json`. No source asset or canonical W04 runtime actor was replaced.
- Open: authored Blend Space/Animation Blueprint/Foot IK and compatible movement clips; UHT/UBT, engine callbacks, input/camera/foot placement, networking, package/playthrough and latency acceptance.
- Next: pull the updated PR #46 branch on the engine host, install the exact plugin in the backed-up UE 5.7 test project and complete `source/p15-combat/Docs/CONTROL_ACCEPTANCE_AR.md`. Keep this work active until engine evidence exists; do not merge as runtime-ready.

## 2026-10-17 input responsiveness claim

- Executing agent: Codex. Scope: P15 bounded combat input buffering and an opt-in movement-input shaping component; portable behavior tests and integration guidance. Preserve canonical W04 movement/input ownership and existing assets.
- Starting revision: 4df1894e179e1e6bdd948de932114f8efb376b10; refreshed from origin before edits.
- Completed: one-entry server buffer with expiry/consume-once/cancellation semantics and an opt-in grounded movement-input component; W04 sources and bindings unchanged.
- Evidence: 155 portable/mocked tests passed (64 compiled shared C++ cases). Unreal compilation, authored animation transitions and visual movement acceptance remain separate open gates.
- Next: compile the optional plugin in the UE test project, bind one movement producer and reset events, then measure keyboard/controller starts/stops/reversals and montage recovery.

## 2026-10-17 montage lifecycle and map integration claim

- Executing agent: Codex; scope: accepted montage playback before stamina/defense commitment, immediate interrupted-action cancellation, component setup diagnostics and a read-only combat-map gate before packaging.
- Continue PR #46 from `8620898077ceac3364d502541a60ffa2c38d949d`; preserve W04 actors and the pinned original GLB inputs.
- Host check: AsusRog offline, last seen 33 hours ago. Local C++/Python checks can run; Unreal/UHT/UBT and authored-motion visual QA remain unavailable.
- Completed: guarded playback acceptance, reentrant request reservation, cancellation that preserves cost/recovery, native montage lifecycle callbacks/client cancellation and teardown cleanup, native setup diagnostics, read-only map gate and build integration.
- Executed: 135 delivery tests passed (44 compiled C++ rule cases, 21 mocked combat-map cases and 70 existing intake/preflight/artifact cases), plus 336 existing CI contracts, 6 AssetForge cases and repository validation. Native Unreal callbacks/diagnostics are uncompiled and map validation has only mock evidence here.
- Next action: install the exact updated plugin in a backed-up UE 5.7 test project, compile UHT/UBT, wire compatible authored combat montages/Slot/sockets/notify, tag the placed test hero `NarisP15Playable`, add a separate damageable Character target, then execute the guarded pipeline and record PIE/packaged encounter evidence. No W04 actor is replaced automatically.

## 2026-10-17 P15 source-asset integration claim

- Executing agent: Codex; scope: actual attached GLB intake, digest/class import contract, pre-import validation and P15 build wiring. Preserve W04 runtime and original source bytes.
- Input: five attached GLBs, their duplicate source archive, instructions and a `.usdz`-named binary whose header is `PXR-USDC`.
- Host check: AsusRog offline (last seen 26 hours ago); engine compilation and playtesting remain blocked.
- Repository baseline for this continuation: P15 branch at `8f54e2124def07e8a4d56bbbe32bbfeed3d1ae7e`; continue the existing review rather than declaring a new completed production phase.
- Completed: inspect all five actual GLBs; repair the missing mesh Skin binding and transposed/incorrect inverse binds in a new prototype copy; preserve original eight inputs; pin hashes/classes; validate all sources before any editor import; wire the same source contract into the Windows launcher; document actual-source and engine boundaries.
- Local verification: 95 P15 behavioral tests, 336 existing CI-contract tests and 6 AssetForge tests passed; repository validation passed. `Reports/source_asset_audit.json`, `source_assets_check.json` and `cpu_bind_verification.json` record actual-file results, separate from mocked editor tests.
- Pending: actual UE 5.7 compile/import, compatible combat montages/slots/sockets, two-client PIE, packaged encounter and profiling. The raw sources are not promoted into the canonical production registry and W04 actors are not replaced.

## 2026-10-16 P15 combat-delivery repair claim

- Executing agent: Codex.
- Claimed scope: the `NARIS_P15_DELIVERY_20261016.zip` combat plugin, importer, build runner and behavioral tests, maintained under `source/p15-combat/`; this is separate from P15 animation archives.
- Preserve canonical W04 gameplay classes; avoid the incoming plugin's duplicate `UNarisCombatComponent` reflection name.
- Validate portable combat rules and importer failure paths locally. Unreal UHT/UBT, Windows packaging and playtests require the offline AsusRog host and remain open.
- Source base: main at `75f9d1886e7a4de5c79a0bb6c723506ff8feb3bc`.
- Completed: isolated corrected P15 combat delivery; renamed reflected component and migration redirect; shared validated rules; montage/notify and server trace source; fail-closed importer; read-only installation/engine/map preflight; fresh package/artifact verification; CI integration and integration README.
- Executed evidence: 61 delivery behavioral tests passed (25 compile/run the shared C++ header, 20 mocked import tests, 8 project preflight tests, 8 package-artifact tests); 336 existing CI-contract tests and 6 AssetForge tests passed; `tools/ci/validate_naris.py` passed.
- Not executed: UHT/UBT/plugin link, PowerShell locally, actual Unreal import/PIE, Windows packaging/launch or performance. The plugin is not auto-enabled in W04.
- Next action: use a backed-up UE 5.7 test project on the engine host; install the exact plugin; wire authored montages/slots/sockets/notify, run the README encounter checklist and guarded Windows pipeline, and retain real logs before closing the gate.

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
- Confirmed constraint: the checked-in Unreal descriptor selects 5.7; Windows PC remains primary. This descriptor read is not engine build evidence.
- Runtime blocker: registered AsusRog remote host is offline, so neither Blender nor Unreal can be executed from this session yet.
- Backend blocker: Neon connector requires a concrete project ID and the repository has no bound .neon/neon.json project metadata; no migration was applied.
- Open issues: Windows compile/package/runtime evidence; actual W04_AshenForest production map; seven core production meshes; approved surface/water master materials + generated instances; 16 Audio + 14 Niagara payloads; 10 production AnimMontages; real Blender-to-Unreal Factory v2 run; Arabic visual/RTL QA; measured hardware performance; strict Shipping RC evidence.
- Missing sources: 18 attachment paths announced for this session were absent; no asset contents were inspected.
- Next action: when Windows is online, run `tools/windows/Invoke-NarisBlenderMasterBuilder.ps1 -ExportCoreAssets` and retain its blend/validation/manifest/export evidence; then compile NARIS_W04Editor, run the W04 Environment Factory bridge and production blockout authoring, retain all reports, and execute Development package/runtime smoke before attempting the strict W04_AshenForest Shipping RC.
- Acceptance: a passing static check alone cannot close engine, DCC import, backend deployment or gameplay gates.
