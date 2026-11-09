# UI-019 — Read-only native UMG state view (avoid per-frame save snapshot copies)

**Date:** 2026-11-09  
**Engine:** Unreal Engine 5.7 / NARIS W04.  
**Branch:** `feature/UI-019-readonly-state-view`, stacked on `feature/UI-018-inventory-compile` (not merged).  
**Baseline:** UI-018 CI GREEN, real UE build and screenshots unavailable.

## Defect / red reproduction
`UNarisSystemMenuWidget::NativeTick()` calls `RefreshInterface()` once per open-menu frame. It used `const FNarisSaveState State = Runtime->GetState();`, while the Blueprint-exposed `GetState()` returns `FNarisSaveState` **by value**, copying the whole object (including `TArray` and `TMap` members) on every menu refresh.

Created `tools/ci/test_ui019_readonly_save_view.py` before C++ changes, connected it to existing `NARIS Unreal Validate` job. At commit `071163cb11946636f0f4d07f1b3bd5a095533c3e`, GitHub run **42566278277 FAILED**: two assertions confirmed no read-only accessor and continued use of the by-value copy in native UMG.

## Minimal fix / green
- `NarisRuntimeSubsystem.h`: added a non-UFUNCTION, C++-only `const FNarisSaveState& GetStateView() const { return State; }`; the existing BlueprintPure `FNarisSaveState GetState() const { return State; }` remains untouched, so Blueprint snapshot and save semantics are preserved.
- `NarisSystemMenuWidget.cpp`: changed just this one menu-site read to `const FNarisSaveState& State = Runtime->GetStateView();`. The reference is used synchronously inside `RefreshInterface()`, on the game thread, and not retained across state mutations.
- All live inventory/equipment, currency, quest, waystone and input callbacks remain as before.
- Source commit `a0799b2dfa875c079233bf10b36266770500330b`; GitHub run **42566353585 SUCCESS**, 51/51 targeted source tests (UI016 17 + UI017 26 + UI018 4 + UI019 4).

## What the test proves and does not prove
Proves: one on-frame snapshot copy removed from actual C++ source; Blueprint method unchanged; no fake UI data. **Does NOT prove measured FPS or memory improvement** because no authorized Windows Unreal host is available. UE Development build, actual PIE, EN/AR RTL screenshots and before/after/diff, 2-client network, BuildCookRun, Project.* automation, -benchmark -fpschart, FPS/RAM/VRAM and Windows EXE **NOT RUN**.

## Risk and rollback
The borrowed reference is only safe while the live `UNarisRuntimeSubsystem` is valid and state is not mutated concurrently; current UI invocation is on the game thread and reference does not escape. Do not expose this API as a Blueprint UFUNCTION reference return or persist it outside the call. Roll back both small header/menu changes together; no original GLB, SVG, approved PNG, map, network or serialized save schema modified. Keep draft until full Unreal quality gate.
