# NARSIC — UI / Runtime Repair Pass — 2026-10-11

## Why this pass exists

Live user feedback superseded the earlier source-only / marker-only UI acceptance: the interface was reported as visually poor and not working reliably.

The earlier packaged QA proved state transitions and widget construction, but did **not** prove that the visible interface on the live workstation was usable, unobstructed, or visually acceptable.

## Field issues observed

- The live Windows game window showed a black scene with `LIGHTING NEEDS TO BE REBUILT` output.
- A Windows Security / Firewall prompt for UnrealGame obstructed the foreground launch.
- The local experimental UMG path used a visibility lifecycle that could leave interfaces hidden while relying on widget Tick to reopen them.
- The canonical repository still used a Canvas menu that displayed a mouse cursor but had no real left-click activation path.
- Public-facing runtime branding was still inconsistent in canonical W04 sources (`CALL OF NARIS` vs the approved `NARSIC`).

## Repairs applied to the canonical repository

### Interaction
- Added a real left-mouse click path in `ANarisPlayerController::InputKey`.
- Added `TryHandleMenuMouseClick()` with viewport-aware hit testing.
- Clicking a visible menu row now selects that row and executes `MenuConfirm()`.
- Menu input mode explicitly leaves the mouse unlocked from the viewport.

### Layout
- Reworked system-menu geometry around a wide tactical frame:
  - max reference width: 1880
  - max reference height: 960
  - safe margin: 32 reference pixels
  - width/height scale uses the minimum viewport axis, so 32:9 does not vertically overflow.
- Added a live operation-status panel bound to real save/runtime state:
  region, checkpoint, active quests, unlocked waystones and inventory count.
- Added unavailable-Continue treatment when no save exists.

### Visual identity
- Public title is now **NARSIC**.
- Updated the shared UI palette toward:
  obsidian / blackened steel / aged bronze / ember / muted bone.
- Removed the old cyan-heavy generic sci-fi emphasis from the system-menu palette.

### Runtime stability / presentation
- Canonical W04 renderer is configured for Lumen/dynamic lighting and static lighting is disabled.
- Android File Server runtime networking is disabled for this desktop production target to reduce irrelevant network/firewall behavior.
- Project metadata and localized title entries use **NARSIC** exactly.

## Evidence state

Repository source repair is complete for this pass.

This document does **not** claim that the repaired source has already passed a new live packaged visual acceptance on AsusRog. Direct workstation control reached its current usage limit before a fresh package + screenshot click-through could be completed.

The UI acceptance gate therefore remains reopened until all of the following pass on the workstation:

1. Win64 Development compile.
2. BuildCookRun package.
3. Main menu visible on first launch.
4. Mouse click-through: New Game / Continue / Settings / Controls / Quit.
5. Keyboard and gamepad navigation.
6. Pause menu and content pages.
7. 16:9 / 21:9 / 32:9 screenshot comparison.
8. No blocking firewall dialog in the intended release configuration.
9. No `LIGHTING NEEDS TO BE REBUILT` overlay.
10. NARSIC exact branding in every player-facing surface.

## Acceptance rule

Do not mark UI/UX complete from log markers alone.

UI acceptance requires **visible + interactive + packaged** evidence.
