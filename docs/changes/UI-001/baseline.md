# CALL OF NARIS — UI-001 Official Visual Direction
Date: 2026-11-04

## Owner approval
The three user-supplied images are approved as **official visual references** for:
- Main Menu: CALL OF NARIS title, Start / Continue / Settings / Exit, gothic fortress, horned warrior.
- Character & Equipment: portrait, levels/XP, stats, equipment grid, active abilities, health/stamina/mana.
- Boss Fight HUD: live boss health bar, quest panel, targeting, player bars and ability cooldowns.

They are design references, **not** actual Unreal UMG assets or runtime screenshots. All characters and world art must retain the original source identity (see `docs/DESIGN_PILLARS.md`).

## Implementation contract
- Use existing Unreal W04 native UMG and game systems instead of replacing gameplay with screenshots.
- UMG buttons must bind to actual game actions and support keyboard/gamepad focus.
- Health, XP, equipment and boss stats must bind to live state; no baked static numbers.
- Arabic layout, RTL/shaping and English localization; safe areas, DPI, 16:9, ultrawide, accessibility.
- Distinct texture import location: `/Game/NARIS/UI/ApprovedReferences`.
- PNG originals are preserved byte-for-byte; install pack includes SHA256 manifest and source files.
- A reference JPEG for main menu masks only the baked button column; manual art cleanup remains required for a production background.

## Device audit
AsusRog was online during inspection. `C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Install-NARIS-UI.cmd` is a **Unity** installer targeting `Game\NARIS\Assets\Resources\NarisUI`, not the canonical Unreal project. It was not executed and must not be treated as Unreal deployment evidence. Canonical source: `unreal/NARIS_W04/NARIS_W04.uproject`, EngineAssociation 5.7.

## Evidence / QA
Local package `NARIS_UI_001_OFFICIAL_HANDOFF.zip`: 3 preserved PNG source references + derived reference JPGs + guarded Unreal Python texture importer + PowerShell staging installer + 5/5 passing offline tests + ZIP integrity PASS.
Unreal editor import: **NOT RUN**. Native UMG widget binding: **NOT IMPLEMENTED IN THIS CHANGE**. Windows BuildCookRun, PIE, Before/After/Diff, multiplayer server+two clients, FPS benchmark: **NOT RUN**.

## Risk + rollback
Avoid rasterizing functional UI onto gameplay and using static boss-fight art as the game world. If source-art installation is attempted, remove only the newly created `SourceArt/UI_Approved/UI-001` directory; existing UMG and all original assets must remain untouched. Do not merge until full QA gate passes.
