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

## Remaining work, ordered by dependency

| Priority | Gap | Evidence required to close |
|---|---|---|
| P0 | Unreal compilation after source repairs | Passing Windows UnrealBuildTool log for NARIS_W04Editor |
| P0 | Actual W04 map and binary game assets | Authored/imported .umap/.uasset files with provenance and successful editor loading; current Content files are contracts/data |
| P0 | Complete W04 gameplay loop | Recorded end-to-end editor playtest, including boss completion and demo end |
| P1 | Save/load and checkpoint recovery | Save/restart/load round-trip under runtime conditions |
| P1 | Animation hit windows, HUD, audio and localization | Integrated assets plus gameplay and EN/AR QA evidence |
| P1 | Windows packaging and performance | Reproducible package, launch test and measured hardware/profile results |
| P1 | Shared host verification | Actual Claude Code startup and continuation using the committed state; adapter presence is not execution |
| P2 | AssetForge export/import, erosion and masks | See the [worldgen contract](production/ASSETFORGE_WORLDGEN.md) |
| P2 | Missing reference attachments | Receive and inspect the 18 announced source files; none were available in this session |

No engine upgrade, new product direction, asset approval or public release is implied by these source repairs.
