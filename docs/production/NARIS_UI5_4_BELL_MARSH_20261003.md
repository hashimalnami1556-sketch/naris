# CALL OF NARIS — UI5.4 Bell Marsh Playable Stage
Verified on AsusRog | Unreal Engine 5.7.4 | 2026-10-03

## Changes
- New map /Game/World/Maps/L_BellMarsh_Playable_V1, built from visually verified EntryRestored foundation: 11 dry-stone segments, 2 teal water volumes (opaque geometry), 26 trees, 8 cairn markers, 3 ruin arches, a stone-bell tower, 6 movable lights.
- Ashen Gate now travels to Bell Marsh after the Gate Warden quest and actual crossing. Smoke-crossing skips autosave.
- Bell Marsh GameMode boot: one wolf companion, three BoneBeast enemies, three BellRelic pickups and checkpoint; avoids spawning Ashen Gate actors.
- Q_BellMarsh: collecting 3 BellRelics and defeating 3 BoneBeasts completes chapter II and unlocks Twilight Keep in chapter-state only.
- HUD changes quest text, objectives and world label for Bell Marsh.
- Backward-compatible save format adds optional WorldPackageName without changing schema version. Continue Journey can load the saved world using a queued load through GameInstance SaveSubsystem.
- First-install GameUserSettings tuned for a 6 GiB VRAM class card: 1600x900 at 60 FPS target, 85 percent resolution scale, medium Lumen/shadows, low reflections. Existing users' settings are not intentionally overwritten.

## Validated
- NARISEditor Win64 Development build succeeded (before applying 6GB profile).
- UE BuildCookRun with -nocompileeditor: WindowsDevelopment_UI5_4_BellMarsh BUILD SUCCESSFUL ExitCode=0, 628 cooked packages.
- NARIS_BELL_MARSH_READY in packaged EXE.
- NARIS_BELL_MARSH_QUEST_COMPLETE Relics=3 Beasts=3 TwilightKeepUnlocked=1.
- NARIS_BELL_MARSH_SMOKE PASS (3 enemies, 3 relics, quest and chapter).
- NARIS_WORLD_TRANSITION_SMOKE PASS: from V9 through gate to BellMarsh V1 in one packaged game session, with no simulated autosave.

## Open issues / honesty
- Visual QA with two Unreal Editor sessions open exhausted RTX 3050 6GB VRAM (~5.8GB in use); gameplay screenshot cannot be approved visually while GPU is over budget.
- Windows Security network permission modal blocks screenshots; no permission was granted.
- New default performance profile is checked into source; still requires a fresh packaged test and GPU profiling to judge real 60fps.
- Full-world save resume across application restarts (Continue Journey) requires an explicit dedicated verification; in-game persistent SaveSubsystem and map path are integrated but not yet proven end-to-end.
- Level is a functional blockout: no true simulated water surface, final AAA architecture, final cinematic animations, authored second chapter cutscene, or final optimization.
- Existing Unreal Editor instances were left untouched to preserve any user-unsaved work. Win64 game-only compile avoids Live Coding lock.
