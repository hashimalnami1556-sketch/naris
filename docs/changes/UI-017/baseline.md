# UI-017 — Six original SVG-derived texture icons in the actual gameplay HUD

**Date:** 2026-11-08  
**Source branch:** `feature/UI-017-combat-hud-icons` based on `feature/UI-016-native-icon-bindings`.  
**Release state:** DRAFT / not merged / not installed in UE5.7.

## Baseline
Before UI-017 the six original SVG icons from WORLD-015 were imported only as preparatory PNG assets. UI-016 added `UImage` brushes to menu buttons, but **the actual combat HUD `ANarisHUD::DrawPlayerVitals()`, `DrawObjectiveCard()` still rendered meters/keybinds without the approved icons**. The 3 approved full-screen reference images must not be embedded as fictitious gameplay UI.

## Scope: actual gameplay C++ change
1. `NarisHUD.h`: add `UPROPERTY(Transient)` map of six original-source `UTexture2D` icon refs; never allocate or load on render tick.
2. `NarisHUD.cpp`: load all six icons exactly once in `BeginPlay` from stable `/Game/NARIS/UI/Icons/{name}.{name}` paths (populated by **UI-016 importer**) and draw via actual `AHUD::DrawTexture` with source PNG alpha blending. Missing icons are optional decoration: existing gameplay labels and bars remain visible.
3. Icon mapping is semantic to actual active game values: **health** → live player HP, **mana** → existing Resonance meter, **energy** → Energy component, **attack** → live keybind attack hint, **defense** → live dodge/parry hints, **map** → real W04 quest objective. No sample game values or unbound fake controls.
4. Adjust vital bars and text inset to leave 28px icon column; save original PlayerOwner input and gameplay behavior. No updates to `GameDefaultMap`, original GLBs or approved 3 PNGs.
5. `tools/ui/verify_ui017_hud_assets.py` is a **read-only editor audit** of the exact six imported 256x256 Texture2D assets. It rejects missing/wrong-class/wrong-dimension assets, writes a receipt when run *inside UE5.7 Editor*, and never treats that as PIE or shipping approval.
6. Add `test_ui017_live_combat_icons.py` (9 source contracts) and `test_ui017_texture_editor_audit.py` (5 behavioral cases) to the existing NARIS Unreal Validate action. This is **14 UI017 tests**, plus 17 unchanged UI016 tests.

## TDD and GitHub evidence
- **RED**: CI failure on branch commit `3e4a9960f66e1d3d1a62b210be5d39ed9ab80013` because the nine combat HUD source tests found no real icon drawing. The original C++ HUD had no gameplay textures.
- **GREEN**: HUD source change commits `dae86b7dd938e42ec6b1f2aeef89a2ae9cd660e9`, `859d5b40367dad310fc10b9f395d1a16f8eeb22f`. One overstrict assertion was corrected to also expect the new nonpositive-size guard in helper.
- **GREEN**: after adding read-only editor-audit behavior tests, GitHub workflow `NARIS Unreal Validate` at `47f30f3275467af779a71423f4f958610f272f31` **PASS**. It executed **17/17 UI016 tests + 14/14 UI017 tests**.
- Original source PNGs/SVGs: unchanged in previous WORLD015/ UI016 artifact, available as `NARIS_UI016_SVG_TO_NATIVE_UMG_INSTALL_KIT.zip` in this chat. Exact hashes independently verified in prior local package checks.
- No Unreal Editor installed or remotely authorized in this environment. C++ compiler, real HUD rendering, actual Texture2D import, world screenshot, PIE and shipping gate **NOT RUN**.

## Quality-gate checklist — incomplete, no merge
- Build UE5.7 Development Editor + BuildCookRun.
- Run `tools/windows/Invoke-NarisUI016.ps1 -PackageRoot <UI016-kit-root> -RunEditor` to install authentic six source textures.
- Run `tools/ui/verify_ui017_hud_assets.py` inside Unreal Python with `NARIS_UI017_AUDIT_REPORT` set; inspect report for 6 correct assets.
- Run front-end and W04 gameplay PIE at 1920x1080 fixed Seed/quality, capture before/after/diff, verify HP/Energy/Resonance and live key mapping update, Arabic RTL, 720p/ultrawide, high contrast, collision, 2-client multiplayer and FPS/memory.
- Merge only after actual editor evidence, new BuildCookRun, automation `Project.*`, and stage release review.
- Do NOT claim an EXE, cooked assets, network sync or visual approval until executed.

## Risks / rollback
- HUD layout can overlap at resolutions other than 1920x1080; test safe zones and A11y.
- Asset source alpha/BlendMode may need an in-editor visual color review.
- Revert UI017 source commits and untracked editor imported icons only after checking other dependencies; original maps/GLBs/UI screenshots unaffected.
