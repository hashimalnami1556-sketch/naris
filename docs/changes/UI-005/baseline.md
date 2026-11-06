# UI-005 — Native inventory information panel

Date: 2026-11-06
Engine target: UE 5.7, W04 Ashen Forest

## Before
The native UMG system menu displayed a generic REGION/CHECKPOINT/JOURNEY STATUS panel while the Inventory page was open. The approved owner image expects equipment and backpack content.

## Change
In `UNarisSystemMenuWidget::RefreshInterface`, select the Inventory branch and draw the **live** saved currency, equipped item names and inventory item names from `UNarisRuntimeSubsystem::GetState`. Show localized empty-state copy; cap visible lists at 5 equipped and 7 stored items and indicate remainder. Retain current region/checkpoint status for other menu pages and all existing mouse/gamepad controller callbacks. Do not fabricate attributes from the reference image or overwrite image assets.

## Evidence
- GitHub source readback: 11 of 11 static contract checks true.
- `tools/ci/test_ui005_inventory_status.py` contains six additional static regression test cases; repository-hosted test runner has **not** been executed.
- Unreal compilation, L10n translation import, Arabic RTL screenshot, before/after/diff, Windows package, network (server + two clients), FPS/memory: NOT RUN.
- Full original-approved character screen not yet visually implemented. Original screenshots are *references*, not clickable widgets.
- Remote Desktop Commander connector currently rejects requests with `link_id must identify an eligible linked account`.

## Gate / risk / rollback
**Draft; do not merge before Unreal integration tests.** Verify text length/layout at 720p, 1080p and ultrawide and Arabic/English. Implement localization in all supported languages. Revert the `NarisSystemMenuWidget.cpp` patch to restore earlier generic right panel if UI QA fails. No gameplay save schema, world map or source mesh changed.
