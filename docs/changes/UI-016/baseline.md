# UI-016 — Real native UMG Texture2D binding for six existing user-requested SVG icons

**Date:** 2026-11-08  
**Engine target:** Unreal Engine 5.7 / NARIS W04.  
**Depends on:** WORLD-015 six source SVG/PNG icons; approved three UI screenshot references.
**Branch:** `feature/UI-016-native-icon-bindings` stacked on WORLD-015; intentionally NOT main.

## Before (verified source baseline)
`UNarisSystemMenuWidget::BuildInterface` created a Unicode `UTextBlock` icon with a diamond ("◆"), placed directly inside `IconPlate`. `RefreshInterface` repeatedly changed only the glyph; it **never created a `UImage` or loaded the six Texture2D exports**. WORLD-015 imported six icon textures into a *generated work-level asset path* but did not link those textures to a functional UMG interface. This defect is independently guarded by `tools/ci/test_ui016_native_svg_icon_contract.py` (written before implementation).

## Implemented on this branch
1. C++ `NarisSystemMenuWidget.cpp/h`: construct a real `UImage` inside each clickable `UNarisMenuRowButton`, retain `UTextBlock` overlay as fallback, and keep all controller click/hover delegates unchanged. Image 34×34 within existing 48×42 icon plate.
2. Cache six source-derived `UTexture2D` assets once at widget construction, retaining strong `UPROPERTY(Transient)` references. Resolve textures from stable, version-independent `/Game/NARIS/UI/Icons/{name}.{name}` instead of the ephemeral `/Generated/World015` path.
3. Context mapping uses combat/menu icons on the front-end and pause home screens. Other pages keep their purpose-specific glyphs; localized button labels remain text for accessibility. Missing icon texture = existing text glyph fallback, not an empty button.
4. New `tools/ui/import_naris_ui016_icons.py` verifies the **exact three approved original PNGs** plus six source SVG and six PNG exports against package manifest **and independently pinned SHA256 hashes** before any Unreal asset mutation. Asset import into the stable `/Game/NARIS/UI/Icons` path refuses an existing directory or conflicting assets, imports one Texture2D per icon and writes `UI016_IMPORT_REPORT.json`.
5. `tools/windows/Invoke-NarisUI016.ps1` validates source hashes offline first; `-RunEditor` is explicitly opt-in, guards against running editor/previous import report and checks the import receipt. No maps or existing source GLB files are changed.
6. `DefaultGame.ini` adds `DirectoriesToAlwaysCook=/Game/NARIS/UI/Icons` so dynamically loaded C++ textures can be included by the Windows cooker after importing, rather than disappearing in packaged builds.
7. Nine static/source UMG contracts and seven importer negative/provenance regression tests committed; new `ui016-native-icons.yml` PR workflow.

## Verified available offline evidence
- Inspected actual `NARIS_WORLD_015_REAL_UE57_SVG.zip` source package and unpacked original six SVG+PNG artifacts.
- Local **27/27** individual digest/PNG alpha/SVG well-formedness and size checks PASS: source three original UI images match SHA256, six SVG hashes match, six PNG hashes match and every icon PNG is RGBA/transparent 256×256.
- Compiling C++ is impossible in this execution environment (no UE5.7 runtime host). GitHub Actions contract result is tracked separately.
- **NO UE5.7 editor run / actual `.uasset` import / screenshot before-after / DPI / Arabic RTL visual verification / BuildCookRun / `Project.*` automation / 2-client network / FPS/VRAM / Windows executable.** Runtime UMG visual result is not confirmed.

## QA and acceptance gates
- On a connected Windows UE5.7 host with the repository checkout + WORLD-015 package extracted: `tools/windows/Invoke-NarisUI016.ps1 -PackageRoot <WORLD015-root> -RepoRoot <repo> -RunEditor` to import the six source icons.
- Restart editor/PIE, inspect main + pause menu click/hover/controller, verify original approved source design, fallbacks, EN/AR RTL, 720p/1080p/ultrawide.
- Run repo validator, full tests, Development Build + BuildCookRun, `Project.*`, server+2 clients, fixed Seed screenshots before/after/diff, FPS/memory. Only then mark green.
- **Do not merge** until tests and visual screenshots exist; no original images replaced. All six SVG source files are already versioned in WORLD-015 and all six PNG export bytes remain in the package.

## Risk / rollback
- Without the exact imported assets, C++ UI falls back to original glyphs; cook directory may warn if empty. This is a **delivery blocker**, not approval for shipping.
- At small viewport sizes the 34×34 image may need DPI or safe-zone adjustment.
- Roll back by reverting this branch (C++ + Config changes); remove the isolated `/Game/NARIS/UI/Icons` folder only after reviewing it for manually added dependencies. No save schema, world maps or original 3D assets touched.
