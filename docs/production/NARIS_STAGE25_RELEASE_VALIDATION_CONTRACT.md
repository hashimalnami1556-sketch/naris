# NARIS Stage 25 — Release Validation Contract (2026-10-26)

This supplements the existing `tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1` (build, cook, archive and strict authoring validation). Do **not** bypass or replace it.

## P0–P5 gates
- P0: deterministic names, approved modular-kit grid, export scale and skeleton validation; imports quarantined before promotion.
- P1: W04 Ashen Forest collision, combat space, line-of-sight and navigation acceptance.
- P2: one rigged hero with complete locomotion, hitbox / Montage Notifies, reactions and death; foot-contact proof.
- P3: Bone Hound + boss runtime AI, GAS/health, differentiated animations and combat encounter.
- P4: Unreal Insights and hardware-bound 60 FPS profiling, animation/VFX/cloth costs, measured frame-time percentiles.
- P5: existing Windows RC script, packaged Windows smoke test, localization, crash and rollback checks.

## Fail-closed evidence
Eight report categories are required: `build`, `map`, `animation`, `combat`, `playtest`, `performance`, `localization`, `crash`. Each requires `status: pass` and a non-empty path to genuine evidence. Performance also requires p5 FPS >= 60 and p95 frame time <= 16.67 ms, defined as *targets* not historical measurements. Gate acceptance requires a human/CI inspection of the actual referenced artifacts; JSON schema validity alone is insufficient.

## Delivery/provenance
Keep immutable build provenance: commit SHA, Unreal build, plugin versions, platform, target hardware GPU/driver, resolution, relevant cooked maps, artifact SHA256, runtime logs, test timestamps, crash reports and rollback point.

**Canonical platform:** single-player Windows PC; multiplayer replication tests are inapplicable unless product scope changes.

## Implemented deliverable
The Stage25 ZIP supplies the Python `validate_release_evidence.py` CLI, blocked sample manifest and four Python unit tests. Offline tests pass (4/4), and the deliberately blocked sample returns exit code 1. **Neither Unreal engine builds nor game runtime tests have been executed by Stage25.**
