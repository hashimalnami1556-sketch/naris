# CALL OF NARIS — MASTER PROJECT

Unified production foundation for the NARIS game.

## Runtime
- Canonical runtime: Unreal Engine 5
- Primary vertical slice: W04 — Ashen Forest
- Current gate: Production foundation; **not Release Candidate**

## Core production characters
- Ashen Vessel
- Celestial Wolf

## First vertical-slice boss
- Bone Beast

## Canonical Vertical Slice flow
Main Menu → Awakening → Forest Entrance → Combat Tutorial → Broken Shrine / Memory Crystal → First Whisper → Ash Gate → Celestial Wolf → Ruined Bridge → Bone Beast Arena → Bone Beast → Reward → Demo End

## Production rule
A system is complete only when **Data → Runtime → UI → Save → QA** works together and has engine evidence.

## Immediate P0 focus
Combat architecture → production animations → Celestial Wolf → Bone Beast → Ashen Forest collision/NavMesh → audio/VFX → save/load → controller → profiling → Win64 package.

## Source of truth
- `data/MASTER_ASSET_REGISTRY.json` — production asset identity/status.
- `docs/NARIS_V2_MASTER_EXECUTION.md` — master execution contract.
- `docs/production/NARIS_VERTICAL_SLICE_AUDIT_2026-10-01.md` — current gap/RC audit.
- `MASTER_MANIFEST.json` and the production bibles under `NARIS_MASTER/`.

Do not promote asset/status gates without validation evidence.
