# NARIS Master Build QA update — 2026-09-27

## Verified on AsusRog
- Unreal Engine 5.7.4 NARISEditor Development build: PASS.
- Automation: `NARIS.Benchmark.ParsesEnemyCount` and `NARIS.FrontEnd.StartsInMenuAndCanStart`: 2/2 PASS.
- `NARIS_QUEST_SMOKE`: PASS for quest, gate, save/load, chapter, accessibility, audio, VFX and checkpoint checks.
- Packaged Windows Development build: PASS; the packaged runtime smoke test also passed.
- Windows Shipping BuildCookRun for all maps: PASS. This is a staging candidate only; visual acceptance and performance certification are still open.
- User audio/accessibility settings now persist; graphics quality calls `SaveSettings`. The smoke test restores accessibility values after checking them.

## Changes synced to this review branch
- `unreal/NARIS_Desktop/Source/NarisCore/Public/NarisUserSettingsSubsystem.h`
- `unreal/NARIS_Desktop/Source/NarisCore/Private/NarisUserSettingsSubsystem.cpp`
- `unreal/NARIS_Desktop/Source/NarisCore/Private/NarisGameModeBase.cpp`

## Before and after (project structure)
Before: project docs and the source/reference folders were flat; archives were retained separately in `Packages/Legacy`.
After: project navigation is grouped under `00_Core` through `08_Integration`, with Unreal live paths (`Source`, `Content`, `Config`) preserved. Build outputs live under `06_Builds/Development` and `06_Builds/Staging`; the 33 local reference images remain under `SourceAssets/References/Images`.

## Release gates still open
- Real Unreal UMG screens, Arabic RTL shaping/font asset, controller navigation and visual review at 1080p/4K.
- Connect stored Master/Music/SFX levels to the actual audio mix.
- Import completed Figma screens; the checked-in Widget Blueprints folder is empty.
- Reconcile this desktop project with canonical W04. This branch has not been merged into `main`.
- Visual playtest and measured FPS/GPU/memory results; final art and end-to-end acceptance.
- Binary Unreal payloads remain local, so this GitHub intake is not a standalone runnable clone.

No overall completion percentage is claimed because the acceptance criteria are not weighted and multiple release gates have not been tested.
