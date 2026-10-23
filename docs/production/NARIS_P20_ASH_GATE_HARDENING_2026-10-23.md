# NARIS P20 - Ash Gate hardening (2026-10-23)

Status: STRUCTURAL QA PASSED; UNREAL RUNTIME NOT VERIFIED.

Non-destructive extension of experimental P18/P19 Ash Gate greybox. Does not supersede canonical W04 Ashen Forest or change Unreal engine baseline.

## Verified locally
- 19 original Python tests passed before changes.
- Four new regression tests failed first, then passed after repairs.
- stage_gate.py validates all four GLB binary structures, SHA-256 against stage_layout.json, spawn positions, and units.
- Unreal staging now fails closed on invalid assets or empty layer imports; uses a separate P20 level and explicitly configures ground/architecture collision.
- 23 of 23 Python tests passed after repair.

## Not verified
Unreal 5.7 import and PIE, actual collision, navigation, rigs, animations, FPS, visual quality, EXE, or console builds.

## Local delivery
NARIS_P20_Fixes_20261023.zip delivered separately in conversation. Includes the full repaired package, scripts, tests and reports.

## Unreal acceptance procedure
1. Back up the Unreal project.
2. Run: python tools/stage_gate.py assets
3. Enable glTF Interchange and Python Editor Scripting, then run unreal/build_ash_gate.py from extracted package.
4. Verify mesh placement, centimetre scale, collision, navmesh and player spawn in PIE.
5. Record runtime evidence before marking approved.

No production build or art approval is implied by structural tests.