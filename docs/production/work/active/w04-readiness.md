---
status: active
last_updated: 2026-10-01
---
# W04 readiness handoff

## 2026-10-09 rendered baseline inspection (05:32-05:37 UTC)

- Executing agent: Codex. Ran the live UE5.7 project on L_AshMap_Assembly with a real D3D12 renderer, 1280x720 window, isolated temporary UserDir and NARISGAMEPLAYSCREENQA. No graphics settings were changed. Host GPU identified as NVIDIA GeForce RTX 3050.
- Examined the engine-generated scene capture and then a separate HUD-inclusive `NARSIC_Gameplay_QA.png`, under `AppData/Local/Temp/NarisCodexVisualQA_20261009/Saved/Screenshots/WindowsEditor`. The first HighResShot excluded HUD; it was not used to conclude HUD absence.
- Observed: hero rendered; scene consists of a flat dark platform, sparse separate assets, oversized bright vertical forms, largely plain surfaces and very large dark shadows. This view does not meet the intended assembled dark-fantasy environment presentation. A still frame cannot diagnose temporal flicker or distinguish every material/lighting cause.
- HUD-inclusive observation: health/stamina at upper left, objective at upper right, resources at lower left; no visible minimap. Read the complete 197-line NarisGameplayHUDWidget.cpp: its BuildInterface creates status/objective/resources/boss/death panels, not a minimap. The earlier W04 minimap implementation is in a different module and is not proof of integration into this live NARIS HUD.
- Source follow-up: current NarisCreature.cpp still selects Idle/Run/Attack through SingleNode playback; no Walk/Trot/Blend references appeared in the inspected source. Imported clips must be verified and wired before claiming their use at runtime. No new clip bindings or rig edits were made in this audit.
- Runtime diagnostics: CesiumRuntime reported an uninitialized EnumProperty for FCesiumMetadataPropertyStatisticValue::Semantic. The level continued loading; this is an outstanding plugin diagnostic, not proof of a crash. Logs retained as Codex_VisualQA_20261009.log and Codex_VisualHUDQA_20261009.log in the live project's Saved/Logs.
- Clarifications: the previous 1007.2-unit navigation result measured the spawned BoneBeast enemy, not wolf gait. TMP caused the build-launch problem; attack playback rate was a separate code correction.
- Acceptance remains OPEN: wolf motion/foot contact, stationary-versus-moving attack timing, minimap spatial correctness, temporal flicker and performance require additional tests. No video inspection or final visual approval is claimed. Priorities: implement the live HUD minimap, verify/wire wolf locomotion clips, and validate the intended assembled level before tuning expensive rendering settings. The current gameplay window was left open for inspection.

## 2026-10-09 build recovery and headless navigation evidence

- Executing agent: Codex. Follow-up supersedes the build blocker recorded below; visual acceptance remains open.
- Root cause found in the remote execution environment: process `TMP` was unset while the user's registered TMP/TEMP directory existed. Build.bat constructs its lock path from TMP, so its waiting message was not sufficient evidence of an active compiler. Restored TMP and TEMP from the user's existing environment values for this invocation only. No engine scripts, system settings or foreign build sessions were changed.
- Cleaned up the verified orphan child of our previous waiting session (parent 17744, child 26380).
- Actual UE5.7 build: NARISEditor Win64 Development succeeded, exit 0, 25.56 seconds. It compiled NarisCreature.cpp, linked UnrealEditor-NARIS.lib/.dll and wrote target metadata. Dedicated host evidence: `Game/NARIS_UE57/Saved/Logs/Codex_AttackRate_Build_20261009.log`.
- Actual runtime smoke: UnrealEditor-Cmd loaded `/Game/NARIS/Maps/L_AshMap_Assembly` with `-game -nullrhi -nosound -unattended -NARISNAVQA` and a separate temporary UserDir. Exit 0, 56.45 seconds including initialization. At 2026-10-09 00:26:13 UTC: `NARIS_NAV_QA_RESULT Pass=1 Travelled=1007.2 TargetValid=1`. Dedicated host evidence: `Game/NARIS_UE57/Saved/Logs/Codex_NavQA_20261009.log`.
- This validates compilation and the existing AI navigation smoke only. NullRHI renders no scene; it cannot establish gait quality, wolf foot contact, attack animation timing, minimap readability or environmental sharpness. No packaged release, W04 engine migration or visual acceptance is claimed.
- Next: rendered playtest of the live scene with stationary/moving attacks, wolf follow transitions, minimap alignment and matched clarity captures. Keep user saves isolated during automated QA.

## 2026-10-09 live UE 5.7 creature correction

- Executing agent: Codex. Scope: preserve the independently edited live NARIS module and record a minimal attack-rate correction. This does not migrate W04 or replace its source.
- AsusRog was online. Re-read `Game/NARIS_UE57/Source/NARIS/NarisCreature.cpp` and confirmed the applied attack-rate change: attacks use 1.0 playback rate independently of locomotion speed. Previously moving attacks inherited 0.9/1.3 rates while the attack-state duration remained fixed.
- Backup from the edit: `NarisCreature.cpp.pre_attack_rate_20261008_2000.bak`. Original file SHA256: `AE90F2F78A3742CE2CBF944CB5CA1B79BA1786F2190BF4528D499AD06904B48F`.
- Minimal transfer patch: `tools/windows/patches/ue57-creature-attack-rate.patch`, relative to the live UE57 project root. It is already applied on AsusRog; do not apply twice or apply to W04. For another matching checkout, first inspect the diff and use `git apply --check --unidiff-zero` before applying with `--unidiff-zero`; back up the target file first.
- Verification: source line was re-read on the host. The NARISEditor Win64 Development build attempt reached only `Build.bat is already running, waiting for existing script to terminate...`. Several other build sessions existed. Only this attempt's waiting session was terminated; other sessions and engine locks were left intact. No successful compile or playtest of this correction is claimed.
- Remaining: direct SingleNode clip changes still lack blending; rig quality, foot contact, attack hit synchronization, minimap visuals and environment clarity need runtime validation. This correction alone does not repair those issues.
- Next: after concurrent builds finish, compile NARISEditor on UE5.7, retain this build's log, and compare stationary/moving creature attacks and locomotion transitions in the actual level. Resolve clip duration versus the fixed attack window from observed animation data.
- Attachment intake: referenced image files are now present locally. The newly attached Blender production prompt contains incomplete generation/animation code; its claimed asset counts and quality are requirements, not produced or verified assets. It was not executed.

## 2026-10-08 local navigation follow-up

- Executing agent: Codex; scope: HUD live player-centered map and portable coordinate tests.
- Replaced fixed pause-map lines with a shared north-up local navigation view, also shown during gameplay. North is world +X; east is +Y. Actor position and heading are sampled on every HUD draw.
- Symbols: player triangle, bonded wolf square, discovered same-map waystone diamond. Out-of-range markers are hidden; glyphs are inset to avoid clipping. Existing save data controls discovery; no new save schema.
- Editable local radius defaults to 5000 cm; HUD display can be disabled independently of the pause-map view.
- This is local navigation, not authored terrain/cartography. Only loaded actors have marker positions. EN/AR source catalogs include the new labels; compilation and RTL visual checks remain pending, along with terrain background, streamed-out landmarks, visual accessibility and runtime performance.
- Acceptance gate: portable center/cardinal/boundary/invalid-input/translation tests; repository static validation; Windows Unreal compilation and gameplay QA remain required before merge.
- Local evidence: map and companion portable C++ tests passed with warnings as errors; repository validator passed after adding EN/AR catalog entries; six AssetForge tests passed; whitespace validation passed. No engine compile/playtest was executed.
- Next: compile and inspect on Windows at 720p/1080p/ultrawide in EN/AR; verify marker alignment, heading, save/load discovery and HUD overlap. Integrate a calibrated terrain layer from the actual level rather than a fabricated illustration.

## 2026-10-08 companion approach correction

- Executing agent: Codex.
- Claimed scope: CelestialWolf ground approach calculation and focused regression tests.
- Preserve: Unreal/W04 engine baseline, asset IDs, combat timing and existing user settings.
- Observed source defect: movement input uses full 3D distance and has a nonzero jump at the acceptance boundary.
- Required evidence: portable calculation tests plus repository validation; Unreal compilation and visual locomotion remain separate pending gates.
- Implemented: planar-only approach input, continuous slowdown outside the acceptance radius, editable slowdown distance, movement-oriented yaw defaults.
- Verified locally: portable C++ test (g++ C++17, warnings as errors), repository validator (52 JSON files), six AssetForge tests and git diff whitespace check passed.
- CI: added the portable calculation test to NARIS CI. This is not an Unreal compile or gait/rig validation.
- Broader static suite: 295/296 passed; test_pause_controller_exposes_controls_page_and_capture_state fails because it expects FInputKeyParams while the unchanged controller header uses FInputKeyEventArgs. Both files match the starting commit; this unrelated baseline mismatch was not modified or hidden.
- Remaining scope: the pause-map renderer still draws fixed schematic lines; no live minimap or terrain source is wired. Hero/wolf production locomotion clips and visual blur diagnosis require the actual Unreal scene and authored assets. No visual or performance acceptance is claimed.
- Next: compile W04Editor on Windows; test follow/guard/track/echo-link approaches on level ground, slopes and stairs at 30/60 fps, including changing targets and existing Blueprint overrides. Then implement a world-coordinate map from verified level data and diagnose blur from matched captures.

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
