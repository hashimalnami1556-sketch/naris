# UI-006 — Single integration branch: approved UI and strict world gate
Date: 2026-11-06

## Change scope
Consolidate the user's three approved UI targets in the **actual Unreal W04 native C++ source** without changing the original 3D assets:
- Front-end `NarisSystemMenuWidget.cpp`: right-side menu anchors (0.71, 0.27, 0.95, 0.83), reduced overlay darkening; preserve original mouse, keyboard and gamepad actions.
- Inventory `NarisSystemMenuWidget.cpp`: show save-state currency/equipped/inventory rows in the right panel; cap visible item rows; no fictitious attributes.
- Combat `NarisHUD.cpp`: top-center boss health bar based on real W04 Bone Beast HP and phase.
- `docs/ui/references/UI-002/manifest.json`: original approved three images with SHA256, **image binaries not committed or imported into Unreal**.
- `tools/ci/verify_ui_world_release.py`: fail-closed preflight for production W04 .umap, default map, exact three source PNG hashes and native UI source hooks.
- `tools/ci/test_ui006_release_gate.py`: five regression cases for correct and failing conditions.

## Baseline / evidence
- Main branch still configures `GameDefaultMap=/Game/NARIS/W04/Maps/W04_Prototype`.
- `unreal/NARIS_W04/Content/NARIS/W04/Maps/W04_AshenForest.umap` was NOT found on GitHub main.
- Therefore **do not force-switch the default map**; running the package with a non-existent default map risks failure.
- Earlier UI-003, UI-004 and UI-005 work was isolated on draft branches; this branch consolidates their **source** changes for review, not their runtime tests.
- The approved PNGs are concept/reference screenshots. Render actual 3D scene and functional UMG widgets rather than flattening them as static clickable controls.
- UI-006 status: SOURCE INTEGRATED ON FEATURE BRANCH, NOT MERGED, NOT INSTALLED.
- Engine / Blender / Windows runtime host unavailable. Unreal build, cook, visual screenshots (before/after/diff), player traversal, L10n/RTL and gamepad, 2-client network and frame metrics **NOT RUN**.

## Required acceptance / release gates
1. Import original approved PNGs via hash-checked reference package (LFS tracked separately) and assemble real art layers into UMG controls.
2. Validate production `.umap` existence and cooked dependencies, then set `GameDefaultMap` after editor validation (not before).
3. Integrate original GLB/FBX/USDZ assets with provenance, actual meshes and collisions. Keep Design Pillars Option 2.
4. Run `python -m unittest discover -s tools/ci -p test_ui006_release_gate.py -v` and repository's established CI validators.
5. Run UE5.7 Development Build, BuildCookRun, `Project.*` automation, a server and two clients, actual Before/After/Diff at fixed seed/res/quality, EN/AR RTL/accessibility and FPS/memory.
6. Promote/merge only when these tests are green and PR includes evidence.

## Risks and rollback
UI might overlap content on ultrawide/720p; fonts, source PNG layering and localization remain incomplete. The default playable map is unchanged. Rollback: revert UI source changes; no source assets nor save schemas have been overwritten.
