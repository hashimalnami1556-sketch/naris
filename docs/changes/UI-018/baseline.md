# UI-018 — Repair undeclared C++ Inventory flag in native UMG

**Date:** 2026-11-09  
**Engine target:** Unreal Engine 5.7 / CALL OF NARIS W04.  
**Change branch:** `feature/UI-018-inventory-compile`, stacked on `feature/UI-017-combat-hud-icons` (base HEAD `f8cd74e611344ce6fc7b989b526d1553abf9cc13`).  
**Scope:** one C++ local variable declaration + four CI regression tests. No world, art, SVG, save, network or default-map change.

## Defect / before
`UNarisSystemMenuWidget::RefreshInterface()` in the prior UI-017 source dereferenced `bInventoryPage` twice (inventory content and status title) but **contained no declaration of this identifier**. This is a native C++ compile-time blocker, though an actual Unreal compiler could not be invoked in this environment.

## RED reproduction
- Added `tools/ci/test_ui018_inventory_compile.py`, using the same repository CI conventions.
- Integrated the four tests into `NARIS Unreal Validate` before changing source.
- GitHub workflow run **42565855915 FAILED** at commit `6176b853b651c24b5683a3c13f1c1636c4c8d12b`; two new tests failed specifically because the declaration was missing. Existing UI016 (17 tests) and UI017 (26 tests) remained green.

## GREEN — minimal source fix
Immediately before `FString Status` in `RefreshInterface` define:
```cpp
const bool bInventoryPage =
    Controller->GetPauseMenuPage() == ENarisPauseMenuPage::Inventory;
```
This controls both inventory contents and its localized title without altering other menu pages or input callbacks. Actual `FNarisSaveState` has `InventoryItems`, `EquippedItems`, `Currency` fields.

- Commit: `6ab646a5a8ed90c502bd2034fa2afcd9d8c2b4b1`.
- GitHub workflow **42565926629 SUCCESS**: UI016 **17/17**, UI017 **26/26**, UI018 **4/4** static tests. The repository's existing additional file/presence checks also passed.
- Total targeted regression cases in those groups: **47/47**.

## Quality gate not passed
- **Unreal Editor actual Development C++ compile: NOT RUN**, host inaccessible. Static checks cannot prove UE API correctness elsewhere.
- **Before/After/Diff screenshots:** NOT RUN, no engine session.
- **BuildCookRun, Project.* automation, network server+2 clients, -benchmark -fpschart, FPS/RAM/VRAM, Arabic RTL screen QA, packaged Windows executable:** NOT RUN.
- **Baseline FPS/Memory:** unknown. **ΔFPS/ΔRAM:** not measured.

## Rollback
Revert the single local variable declaration if another code path replaces the Inventory page state; no original user SVG/PNG/GLB data or gameplay save schema modified. Keep PR in DRAFT and do not merge without full Unreal quality gate.
