# Desktop NarisCore intake candidate

This UE5.7 project snapshots the tested Windows prototype from 2026-09-27. It does not replace the canonical `unreal/NARIS_W04` implementation.

Open NARIS.uproject with UE5.7 and build NARISEditor. Default boot opens the menu; -NarisDirectPlay explicitly enters gameplay; -NarisQuestSmoke runs the headless-compatible gameplay smoke. Fetch Git LFS assets before opening the map.

Source, Config, imported Content, pipeline scripts and historical Tests are included. Engine binaries, packaged releases, local Blender source and exchange payloads are not included. Existing pipeline scripts may reference the original Windows path; migrate these before running them elsewhere.

The original test reports predate this intake. Use ../../docs/production/desktop-runtime-evidence.json for the new test, and ../../docs/production/desktop-integration-audit-20260927.md for gaps. Headless smoke does not validate visuals, sound output or production readiness.

IMPORTANT: text-only GitHub intake; binary uploads are pending. See BINARY_ASSETS_PENDING.md. Local desktop testing used real assets; the source-only checkout cannot reproduce that smoke yet.
