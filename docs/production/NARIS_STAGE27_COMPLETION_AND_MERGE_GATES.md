# Stage 27 — Safe structure integration and completion gates

2026-10-27. Baseline: `NARIS_COMPLETE_PROJECT_STRUCTURE_V1.zip`, 134 ZIP entries; canonical UE project `unreal/NARIS_W04/NARIS_W04.uproject`.

## Delivered
- A deterministic **non-destructive** installer for the prior structure package: dry-run, SHA256, conflicts flagged, new files copied exclusively, production GLB prototypes ignored.
- 2 passing unit tests (conflict handling and ZIP traversal prevention).
- Detailed release-gate and build handoff in downloadable `NARIS_STAGE27_SAFE_INTEGRATION_AND_COMPLETION.zip`.

## Do not claim
The structure overlay is **not yet installed on the Windows workstation**; `AsusRog` is offline. The Stage26 Ashen Forest candidate is still GLB, not a validated shipping `.umap`. There is no verified Windows EXE. Repository documentation changes do not constitute playable runtime integration.

## Execution order
1. Source audit + safe dry-run overlay into the canonical repo.
2. Author actual `W04_AshenForest.umap`, with 6 required zones, collision, NavMesh, seven required actor labels and four actor classes; run `naris_validate_shipping_map.py`.
3. Rig/animate hero, Veil Mother, Bone Hound, validate skeletal meshes and in-game motion.
4. Close playable loop and QA, collect engine reports.
5. Execute `tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1` on Windows UE5.7 and verify shipping executable and runtime logs.

The source-of-truth Unreal repo must not be replaced by the structure template. The integration tool is in the downloadable companion ZIP; source is not yet mirrored to GitHub.
