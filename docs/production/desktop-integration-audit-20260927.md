# Desktop and service integration audit — 2026-09-27
Question: what actually exists, runs and remains missing across Windows, GitHub and design?
Canonical expectation: main / unreal/NARIS_W04; a desktop prototype is not proof of W04 Shipping readiness.

| Surface | Verified evidence | Classification / next action |
|---|---|---|
| Windows | AsusRog reachable; UE5.7 installed; Blender --version = 5.2.1 LTS | Previous offline blocker superseded |
| Desktop | C:/Users/Admin/NARIS; NarisCore; base commit 7e9904a; existing HUD/GameMode edits retained | Separate implementation, not a W04 migration |
| Git | Desktop master diverged from main: 22 desktop-only and 732 main-only commits at audit | Intake under unreal/NARIS_Desktop on review branch; do not overwrite main |
| Engine | NARISEditor Win64 Development compile succeeded in 36.86 seconds | Fresh compile evidence for desktop only |
| Runtime | Headless editor game quest/save/checkpoint smoke PASS; player save hashes unchanged | Not graphics, audible sound, controller playtest or packaged-build evidence |
| World data | 9 zones, 5 travel nodes, 9 encounters, 3 quests, 6 objectives; validator PASS | Structured data, not nine finished levels |
| Content | 82 uassets, one umap, 34 CSVs; UI directory has no files | Imported prototype assets, not final art approval |
| DCC | 10 blend files; 20 FBX and 3 GLB exports found | Existing source/export files; no new Blender authoring performed |
| Figma | Live file has only 00_Foundations and a cover/color frame | Prior three-page/UI handoff claim contradicted by live metadata |
| Linear | Existing Data & Integration project and HA-24/HA-25 found | Link audit and unresolved convergence work |
| Attachments | 18 files accessible: 14 images, 2 PDFs, 2 MP4s; images opened | Reference inputs only; not imported into Unreal |
| Tamarind Bio | Molecular/protein workflow | No applicable game-production task; no scientific jobs submitted |

## Repairs and evidence
- Smoke checkpoints now use NARIS_SmokeCheckpoint; test cleanup no longer deletes NARIS_Auto.
- Save load rejects unsupported schema and non-finite transform/vital values before player mutation.
- Existing default-menu / explicit -NarisDirectPlay / -NarisQuestSmoke behavior preserved.
- Intake DefaultEngine.ini excludes the device-local Android file-server token.
- File-level intake hashes: [manifest](desktop-intake-manifest.json). Runtime: [evidence](desktop-runtime-evidence.json).

## Blocking gaps
Reconcile NarisCore vs W04 systems; design and implement real menus/settings/inventory/map/quest UIs with Arabic RTL and controller focus; persist/apply desktop accessibility/audio settings; complete save integrity/migrations/rolling slots; replace blockouts with approved rigged art/materials/montages/audio/VFX; verify production map; measure GPU/frame-time performance; package and perform a 10–15 minute visual playtest. Figma currently supplies foundations only. Fresh packaged and Shipping evidence remains absent.

## Publication limitation
Desktop push returned 403 due to wrong local Git account. GitHub connector published text/source only; LFS assets and archived ZIPs remain local. See ../../unreal/NARIS_Desktop/BINARY_ASSETS_PENDING.md.
