# UI-004 — Boss HUD top-center alignment

## Why
The owner-approved combat screenshot places the boss health bar near the top center; the actual W04 native HUD drew it at the bottom center, potentially overlapping abilities and actions.

## What
Change only `ANarisHUD::DrawBossHUD` Y position from `Canvas->ClipY - Safe - H` to `Safe + 12.f * Scale`. Keep W04 actual Bone Beast health, phases and phase text intact; retain the original 3D identity and gameplay values, not illustrative numbers from the screenshot.

## Evidence and test limits
- GitHub readback confirmed seven source-level invariants (placement, centering, active encounter, live HP, phase, safe ratio).
- `tools/ci/test_ui004_boss_hud.py` added with four static regression test cases. Not executed inside the checked-out repository in this environment.
- Before/After/Diff screenshot capture: NOT RUN.
- Unreal Engine 5.7 build, UMG/Canvas visual verification, DPI/RTL, server + two clients, FPS/memory and packaged Windows build: NOT RUN.
- Remote Desktop Commander connector currently returns `link_id must identify an eligible linked account` and no local Unreal Editor is available.
- This is a code change staged on an isolated feature branch, not installed in the player's copy.

## Risk / rollback
Risk: top-center health bar may overlap compass or viewport-specific overlays; verify 16:9 and ultrawide in actual engine. Rollback by reverting this single native HUD position change.

## Next
Run documented repository validator, scoped UI static test, Unreal Development + BuildCookRun, automation and network tests, before/after/diff, frame time benchmark. Review and merge only with a green quality gate.
