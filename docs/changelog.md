## 2026-11-08 — UI-017: six original SVG icons in active W04 combat HUD
- **Why:** UI-016 connected six Texture2D icons to native menus but actual `ANarisHUD` gameplay meters and objective had no icon bindings.
- **What:** one-time six-icon loading from stable source-approved paths; actual health, resonance, energy, action hints and quest UI show original PNG alpha derived from SVG; maintain real component values and input mapping; optional missing texture leaves original text/values. New read-only editor asset audit rejects 256px dimension/class/missing-asset errors.
- **Evidence:** reproduced missing implementation in CI RED, then source HUD patch and 19 new UI017 contracts + 17 UI016 regression tests (36 total); NARIS Unreal Validate PASS in GitHub.
- **Release blocker:** no UE5.7 Editor compilation, PIE/UMG visual screenshot, 2-client network, before/after/diff, performance or Windows BuildCookRun. No main merge.
- **Rollback:** revert isolated UI-017 commit only; do not modify original user art or project maps.
- **Tracking:** `docs/changes/UI-017/baseline.md`; PR #104.

# NARIS development changelog (source changes; not shipping releases)

## 2026-11-08 — UI-016: six original SVG → native UMG image bindings
- **Why:** WORLD-015 imported six PNG textures only as unused assets; the clickable native UMG menu still displayed text-symbol placeholders.
- **What:** Added real `UImage` icons to menu buttons, stable six-Texture2D resolver, selectable tint and text fallback; original mouse/gamepad handlers and Arabic/English labels remain. Added pinned source-image hash importer, protected PowerShell run command, and icon directory cook configuration.
- **Evidence:** 17/17 UI-016 GitHub static/import security tests PASS, 15 approved SVG/PNG/image hash checks PASS in independently extractable binary kit, tamper test PASS.
- **Not verified:** UE5.7 C++ compile, .uasset import, PIE visual/RTL, screenshots, actual FPS/VRAM, network and Windows BuildCookRun. **Draft only; no main merge.**
- **Rollback:** Revert UI-016 feature changes, review and remove only stage-specific imported icon assets after checking dependencies. Preserve original art and maps.
- **Links:** Pull request #103; `docs/changes/UI-016/baseline.md`; `docs/changes/UI-016/qa_report.json`.

