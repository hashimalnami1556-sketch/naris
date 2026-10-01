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

## Audio production update — v2.1
The master now includes an adaptive audio specification under `15_AUDIO/`:
- `AUDIO_BIBLE.md` — leitmotifs, OST slate, boss phases, ambience and mix rules.
- `AUDIO_EVENT_MAP.json` — runtime-facing states, buses and initial event contract.
- `AUDIO_PRODUCTION_CHECKLIST.md` — source, loop, spatial, mix and QA gates.

Current status: **specification ready; final WAV/MP3 production assets are pending generation/recording and listening QA.**

## UI4.1 production update — 2026-10-01

- Guarded production patch: `14_UI_UX/releases/UI4_1/`.
- Verified predecessor runtime evidence: packaged Windows UI3 launched through the front-end and runtime readiness gates.
- Patch automation provides timestamped backup, rollback, NARISEditor build, Windows Development packaging, EXE launch and log acceptance checks.
- Acceptance rejects Direct Play regression, fatal/load failures and missing front-end/runtime readiness markers.
- Full Pause / Inventory / Map / Quest source integration remains pending against the live local source tree; no Unreal binary assets are fabricated.
