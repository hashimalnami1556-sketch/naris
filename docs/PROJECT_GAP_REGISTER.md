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
- Presentation bindings v2 defines deterministic target paths for all 35 required payloads. Current real bindings are 0/35; strict Shipping RC rejects any remaining unbound payload.

## Remaining work, ordered by dependency

| Priority | Gap | Evidence required to close |
|---|---|---|
| P0 | Unreal compilation after source repairs | Passing Windows UnrealBuildTool log for NARIS_W04Editor |
| P0 | Actual W04 map and binary game assets | The bootstrap can generate smoke .umap/.uasset files after an editor build, but no successful generated/editor-loaded binaries are committed evidence; production-authored assets remain required |
| P0 | Complete W04 gameplay loop | Recorded end-to-end editor playtest, including boss completion and demo end |
| P1 | Save/load and checkpoint recovery | Runtime smoke now also verifies quest steps and checkpoint world location; hero respawn is implemented. Close only after packaged Windows save/restart/load/respawn evidence |
| P1 | Animation/presentation/HUD/localization | Hero/Wolf/Boss impact hooks, localized quest HUD, cue bus and deterministic binding paths exist; 35/35 presentation payloads remain unbound and authored animation/Niagara/audio/camera + EN/AR/RTL runtime QA remain required |
| P1 | Windows packaging and performance | BuildCookRun/launch/profiling pipeline is scripted; close only with a successful Windows package artifact, bilingual launch result and measured CSV/GPU/LLM evidence |
| P1 | Shared host verification | Actual Claude Code startup and continuation using the committed state; adapter presence is not execution |
| P2 | AssetForge export/import, erosion and masks | See the [worldgen contract](production/ASSETFORGE_WORLDGEN.md) |
| P2 | Missing reference attachments | Receive and inspect the 18 announced source files; none were available in this session |

No engine upgrade, new product direction, asset approval or public release is implied by these source repairs.
