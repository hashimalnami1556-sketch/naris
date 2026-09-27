# NARIS current work

Updated: 2026-09-27

- Objective: maintain a shared, evidence-based project KB and unblock the Windows W04 vertical slice.
- Human decision owner: project owner (repository user).
- Executing agent: shared-agent integration pass active for Figma/Blender/Neon and W04 readiness.
- Current work: [Desktop reconciliation](docs/production/work/active/desktop-integration-20260927.md); [W04 follow-up](docs/production/work/active/w04-readiness.md).
- Source routing: [knowledge sources](docs/production/knowledge-sources.md).
- Production readiness: [production status](docs/PRODUCTION_STATUS.md).
- Work navigation: [work index](docs/production/work/index.md).
- Integration contract: [Figma, Blender and Neon](docs/production/INTEGRATIONS_FIGMA_BLENDER_NEON.md).
- Figma: live file created and structured at https://www.figma.com/design/lYSmWwGHXCEXODKpG9bpJH.
- Blender -> Unreal bridge: exchange schema, Unreal Python importer, and Windows smoke-test script are checked in. Ashen Forest Factory v2 now has a dedicated end-to-end launcher that generates a UV-safe canonical .blend source, then reuses the registry-gated FBX/GLB + manifest + Unreal import bridge.
- W04 source progression now covers interaction; Waystone checkpoint ID/location + respawn; Memory Crystal -> FirstWhisper; Corrupted Heart quest steps 1-4; Ash Gate persistence; Celestial Wolf bond/modes/animation-driven attacks; arena auto-entry; Bone Beast autonomous phase attacks; quest completion; DemoEnd persistence; and localized HUD objectives.
- Combat production pass adds real incoming-hit defense routing, timed Parry/Dodge windows, five-Essence cycling, pause/resume input, and native animation hit-window/impact notifies with a smoke-only immediate fallback.
- UI/settings readiness: native front-end + pause/settings/controls flows exist in ANarisPlayerController/ANarisHUD; controller remap covers the 11 core W04 actions; NarisGameUserSettings persists graphics/audio/accessibility controls with EN/AR localization. Presentation audio now routes explicitly through SFX/Music/Voice buses using Master × selected bus volume.
- Subtitle readiness: NarisSubtitleSubsystem is time-bounded and data-driven; HUD respects subtitle enabled/scale. Memory Crystal accepts authored FText subtitle content, but no unauthored First Whisper dialogue is hard-coded.
- A packaged runtime smoke director now drives Waystone -> Memory Crystal -> Ash Gate -> Celestial Wolf -> Bone Beast -> DemoEnd, verifies Corrupted Heart steps and checkpoint location, then performs an isolated Save -> New Game -> Load round-trip before bilingual launch smoke.
- Presentation readiness: shared cue bus/profile authoring exists; all 35 required VFX/AUD/Camera IDs are registered with deterministic targets. Five CameraShake payloads are bound to native C++ classes; 30 remain unbound (16 Audio + 14 Niagara VFX). Every audio cue now declares sfx/music/voice routing. Development smoke permits explicit unbound payloads; Shipping RC rejects them.
- Animation readiness: 10 production W04 AnimMontages are registry-backed with deterministic Unreal paths. The Unreal validator checks asset class, required Hero/Wolf/BoneBeast impact notifies, and positive Hero attack-window duration. Development reports unresolved animations; Shipping RC rejects any unresolved/invalid montage.
- Core production asset readiness: Ashen Vessel, Celestial Wolf, Bone Beast, Waystone, Memory Crystal, Ash Gate and Sword of Poem have deterministic Unreal targets and a technical gate for materials, LODs, Skeleton/PhysicsAsset, static collision, Nanite state and LOD0 triangle evidence; core static meshes are capped at 4 material slots and Ash Gate uses the documented 22k LOD0 triangle budget.
- Material readiness: all 10 Ashen Forest material-library entries map to canonical NARIS-W04-MAT IDs and deterministic MaterialInstanceConstant targets. M_MASTER_SURFACE/M_MASTER_WATER capabilities, blend modes and PBR parameters are validated; automation may create/update instances only after approved masters exist and intentionally does not fabricate simplified master materials.
- Presentation intake: 16 audio payloads have deterministic WAV paths, production SFX prompts and validated 48 kHz / 24-bit PCM import rules including digital-silence and -1 dBFS peak checks; 14 Niagara payloads are rejected if the bound system has no emitter handles.
- World assembly readiness: canonical six-zone Ashen Forest requirements are data-driven from LEVEL_LAYOUT. W04_AshenForest_Blockout can be authored automatically for production assembly, while Shipping is hard-separated to /Game/NARIS/W04/Maps/W04_AshenForest and rejects DEV_*, BLOCKOUT_* and RuntimeSmokeDirector content plus missing navigation/lighting/progression actors.
- Environment runtime contract: Factory v2 is authoritative for runtime generator dimensions (1m snap grid, 4m floor module, 3.5m height, 128m streaming cell). The Blender factory reads this JSON directly; prior conflicting grid/LOD metadata was removed and legacy Wave2/Wave3 values remain reference-only unless profiling justifies a migration.
- Unreal editor scripting prerequisites are enabled in the .uproject: PythonScriptPlugin and EditorScriptingUtilities.
- Windows authoring bootstrap can generate the smoke W04_Prototype.umap and DA_BoneBeast_Smoke.uasset after a successful editor build; these binaries are not currently committed evidence.
- Windows package pipeline: Development = build editor -> author smoke map/boss -> validate animations/core assets -> author+validate material instances -> import/resolve presentation payloads -> compile EN/AR -> BuildCookRun Prototype -> packaged progression/save-load smoke -> EN/AR launch -> fatal-log/crash QA -> CSV/GPU/LLM capture. Shipping RC = strict animation/core-asset/material/presentation gates -> strict W04_AshenForest production-map validation -> Shipping BuildCookRun -> artifact/report.
- Verified CI evidence: NARIS CI run 35904765067 success; Content Validation run 35904765117 success; Unreal Validate run 35904765189 success. Windows self-hosted execution remains manual and unverified.
- Static evidence: NARIS CI run 35855364699 passed MCP TypeScript build, Unreal project integrity, repository validation and PowerShell bridge parsing.
- Neon: core PostgreSQL schema contract is checked in; no remote project/branch is bound yet, so no migration has been applied.

Do not treat static validation, Figma design, Blender source/export contracts or Neon schema files as engine/runtime evidence. The checked-in Unreal descriptor selects 5.4; changing that baseline needs an explicit migration and build evidence.

## Verified desktop audit — 2026-09-27
- AsusRog is online; UE5.7 and Blender 5.2.1 are available. Desktop NarisCore differs from canonical W04.
- Desktop editor compile and headless quest/save/checkpoint smoke passed; player saves unchanged. W04 packaging and visual QA remain unverified.
- Attachment files are now accessible in the chat workspace. They are references, not imported engine assets.
- Live Figma metadata shows only 00_Foundations with a cover/color frame; earlier multi-page handoff claims are superseded.
- Next: review desktop intake, reconcile with W04, then run canonical Windows production gates.
- Evidence and remaining gaps: [desktop audit](docs/production/desktop-integration-audit-20260927.md).
