# CALL OF NARIS — Official UI-001 Visual Direction

**Owner-approved on 2026-11-04.** Canonical target: Unreal Engine 5.7, W04 Ashen Forest. This locks the **visual reference direction** for main menu, character/equipment screen and boss gameplay HUD. It does not certify working UMG widgets, runtime installation or a packaged build.

## Approved screen sources (unaltered, SHA256)
| Screen | Reference filename | Source px | SHA256 |
| --- | --- | --- | --- |
| Main Menu | `6aa9381f-5d3d-4061-afcf-280a0fe9c19b.png` | 2048×1152 | `8d216d0a12d39e76a127ac00e20a121b0ca4833be873b00cddf170708e48882f` |
| Character / Equipment | `24a4fb66-1350-4dc4-90c2-be86cc118453.png` | 1672×941 | `ff2e0f04146edeb7c9ce75e624e9c5738d0e576b6b4c86a45e6e008a0b9e9f71` |
| Boss Encounter / HUD | `eedd2359-cd3f-4a0f-9ca2-6398b6c627a7.png` | 2048×1152 | `19734e1aa77206378c915e39d2505d941cc6de4f962b5bd270636ba2ddaa25d6` |

The source PNG bytes are preserved in separate user-downloadable package `NARIS_UI_001_OFFICIAL_REFERENCES.zip` with a manifest, SHA256 tests and Unreal reference-texture importer. They are **reference art**, not native `.uasset` or functional buttons.

## Required functional interpretation
- **Main menu:** cinematic game-scene background, title on right, `ابدأ اللعبة`, `متابعة`, `الإعدادات`, `خروج`. Continue must be disabled without save; real focusable UMG widgets; input/controller and EN/AR support.
- **Character screen:** translucent overlay over a running scene; player portrait/name/level, actual attributes, equipment slots, active abilities, tabs and Health/Energy/Mana. All values bound to gameplay state, not hard-coded from the reference.
- **Boss HUD:** gameplay-visible world, objective, boss health from server-authoritative state, player health/energy/mana, ability keybindings and cooldowns; reduce obstruction and respect safe areas.

## Existing project integration points
Reuse existing native HUD in `unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHUD.h`, existing UI4.1 launcher/rollback and `NarisGameUserSettings`. Use true UMG Widget Blueprints rather than placing screenshot rectangles over gameplay. Preserve original asset artistic identity. No parallel project or engine fork.

## Install and QA gate
1. Import approved PNGs as **reference Texture assets only** under `/Game/NARIS/UI/ApprovedReferences`, without overwriting any existing asset (the package supplies guarded editor import tooling). A reference texture import is not a functional UI install.
2. Build separate interactive UMG widgets connected to existing gameplay, menus, save, and localization systems; test layout at 16:9, 16:10 and ultrawide, AR RTL and EN LTR, keyboard/gamepad, focus and accessibility.
3. Capture reproducible UE Before/After/Diff; run UE 5.7 BuildCookRun, `Project.*` automation, server+2 clients, FPS chart, logs and rollback.
4. Do not merge until all quality gates pass. Do not alter `main` or call the screenshots a shipped game.

**Current evidence:** Reference images SHA-verified; local manifest tests 3/3 PASS; Python syntax check and ZIP integrity PASS. Unreal/UMG integration, Windows installation, runtime and benchmark: **NOT RUN** because Remote Desktop Commander access currently fails with an ineligible linked-account error.

**Rollback:** remove only new reference textures from `/Game/NARIS/UI/ApprovedReferences`, revert changes through Git; do not delete existing HUD/menus.

Reference: https://dev.epicgames.com/documentation/en-us/unreal-engine/umg-user-interface-designer-for-unreal-engine
