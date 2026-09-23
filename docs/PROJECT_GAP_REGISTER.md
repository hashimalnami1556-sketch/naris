# NARIS Project Gap Register

Updated: 2026-09-23. Evidence: repository source inspection and static tests. Engine execution is unverified.

## Corrections to the previous snapshot

The earlier register incorrectly described the repository as containing only README/assets/docs and reported the Unreal project, C++ tree and Gameplay Tags as missing. These now exist:

- [Unreal descriptor](../unreal/NARIS_W04/NARIS_W04.uproject), selecting EngineAssociation 5.4.
- [C++ source](../unreal/NARIS_W04/Source/), including player, companion, combat and boss components.
- [Registered Gameplay Tags](../unreal/NARIS_W04/Config/DefaultGameplayTags.ini).
- [CI workflow](../.github/workflows/naris-ci.yml), including a manually invoked self-hosted Windows build job.

Presence is not proof of successful compilation or correct gameplay. Historical claims remain available in Git.

## Repairs completed on 2026-09-23

- Removed redundant nested Game/Editor TargetRules files; retained the equivalent Source-root definitions.
- Removed the second NARIS_W04 module registration; retained the primary game module.
- Added static checks for duplicate/missing targets and module registration, plus empty C++/header/rules files.
- Fixed the Unreal workflow's empty-file check, whose final `|| true` could mask failure.
- Added AssetForge zero-count and invalid-octave regression coverage and CI execution.
- Added shared Codex/Claude knowledge routing and explicit handoff ownership.
- Removed the isolated legacy Bone Beast/phase path and added duplicate reflected-enum detection.
- Added source-complete W04 smoke progression contracts through DemoEnd, including interaction, save recovery, companion gating, real lock-on melee damage and native smoke HUD.
- Added Unreal Python authoring bootstrap for W04_Prototype/DA_BoneBeast_Smoke generation and a Windows BuildCookRun/package/bilingual launch-smoke pipeline with CSV/GPU/LLM capture requests.
- Added EN/AR localization catalog coverage checks and Windows localization compilation before cook.
- Added packaged runtime progression/save-load smoke reporting using the actual W04 progression actors.
- Added timed Parry/Dodge defense windows, five-Essence cycling, pause/resume, and native hero attack-window/impact animation notify hooks; smoke fallback reuses the same hit path.
- Corrupted Heart now persists steps 1-4 across Memory Crystal, Ash Gate, Celestial Wolf and Bone Beast, with localized EN/AR HUD objectives and packaged save/load checks.
- Waystones now persist checkpoint world location; hero death schedules respawn at the checkpoint and restores health/poise/energy/movement/input.
- Boss arena entry now auto-starts the encounter for the local player; Celestial Wolf and Bone Beast attacks use animation-driven impact commit paths with smoke fallbacks.
- Presentation bindings v2 defines deterministic targets for all 35 required payloads. Five CameraShake payloads are bound to native C++ classes; 30 remain unresolved (16 Audio + 14 Niagara VFX). Strict Shipping RC rejects unresolved payloads.
- Added persistent NarisGameUserSettings plus native Pause/Settings navigation and localized HUD overlay for graphics, audio and accessibility controls; SFX and camera-shake settings now affect the presentation bus.
- Added deterministic audio source/generation contracts and WAV validation for 48 kHz/24-bit PCM, digital silence and -1 dBFS peak ceiling before automated Unreal import.
- Added native Niagara non-empty validation; bound VFX systems with zero emitter handles are rejected during resolution/profile authoring.
- Added native front-end, pause/settings and controller-remap flows with EN/AR localization; remapped interaction prompts read the live action key instead of a fixed keyboard label.
- Added data-driven subtitle runtime/HUD integration; subtitle enabled/scale settings are honored and unauthored First Whisper dialogue is not fabricated in C++.
- Added explicit SFX/Music/Voice presentation audio routing; every audio cue must declare a bus and runtime volume is Master × selected bus.
- Registered 10 required production W04 AnimMontages and added Unreal animation validation for class, required hit/impact notifies and Hero hit-window duration; strict Shipping RC rejects unresolved/invalid animations.
- Added Windows launch log/crash QA that rejects new fatal errors, unhandled exceptions, assertions, low-level fatals, ensures and crash artifacts from the smoke window.
- Added a core production-asset gate for Hero/Wolf/Bone Beast/Waystone/Memory Crystal/Ash Gate/Sword of Poem: deterministic Unreal targets plus materials, LODs, Skeleton/PhysicsAsset, collision, Nanite/triangle evidence and documented material/triangle budgets.
- Separated Development maps from Shipping. W04_Prototype remains runtime-smoke only; W04_AshenForest_Blockout is an automatically authored six-zone production assembly map; Shipping must validate and cook W04_AshenForest with no DEV_/BLOCKOUT_/RuntimeSmokeDirector actors.
- Added the canonical Ashen Forest environment runtime contract and corrected Blender Factory v2 to read snap grid/module/height/streaming/collision/LOD policy directly from its JSON source. The factory can now UV unwrap, save the canonical .blend and run through the existing registry-gated Blender->Unreal bridge.
- Added canonical registry identities and deterministic Unreal MaterialInstance targets for all ten W04 material-library entries. Master-material capabilities/blend modes and PBR instance values are validated; instances can be authored automatically after approved M_MASTER_SURFACE/M_MASTER_WATER assets exist, but simplified masters are not fabricated.

## Remaining work, ordered by dependency

| Priority | Gap | Evidence required to close |
|---|---|---|
| P0 | Unreal compilation after source repairs | Passing Windows UnrealBuildTool log for NARIS_W04Editor |
| P0 | Actual W04 production map and binary game assets | W04_Prototype and W04_AshenForest_Blockout authoring are scripted, but no successful editor-generated binaries are runtime evidence here. Shipping specifically requires a validated /Game/NARIS/W04/Maps/W04_AshenForest plus the gated core production assets |
| P0 | Complete W04 gameplay loop | Recorded end-to-end editor playtest, including boss completion and demo end |
| P1 | Save/load and checkpoint recovery | Runtime smoke now also verifies quest steps and checkpoint world location; hero respawn is implemented. Close only after packaged Windows save/restart/load/respawn evidence |
| P1 | Animation/presentation/material/HUD/localization | Front-end/pause/settings/controls, data-driven subtitles, combat impact hooks, explicit audio buses and localized HUD exist. 5 camera payloads are bound; 16 Audio + 14 Niagara VFX + 10 production AnimMontages remain unresolved. Ten material-instance targets are defined, but approved surface/water masters and runtime-authored instances still need Windows evidence. EN/AR/RTL runtime QA remains required |
| P1 | Core art/technical assets | Seven W04 core meshes have deterministic technical gates but remain unresolved production content until actual Skeletal/Static Mesh assets pass LOD/material/skeleton/physics/collision/Nanite/triangle validation |
| P1 | Windows packaging and performance | BuildCookRun/launch/fatal-log+crash QA/CSV-GPU-LLM pipeline is scripted; close only with a successful Windows artifact, bilingual launch result, clean runtime logs and measured hardware evidence |
| P1 | Shared host verification | Actual Claude Code startup and continuation using the committed state; adapter presence is not execution |
| P2 | AssetForge export/import, erosion and masks | See the [worldgen contract](production/ASSETFORGE_WORLDGEN.md) |
| P2 | Missing reference attachments | Receive and inspect the 18 announced source files; none were available in this session |

No engine upgrade, new product direction, asset approval or public release is implied by these source repairs.
