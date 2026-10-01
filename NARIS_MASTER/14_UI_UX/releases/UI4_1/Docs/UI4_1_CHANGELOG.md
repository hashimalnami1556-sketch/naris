# UI4.1 changelog
- Corrects the previous UI4 package, which contained documentation only.
- Adds guarded installer workflow with timestamped backups.
- Adds rollback support.
- Adds Unreal 5.7 build/cook/stage/pak/archive automation.
- Adds packaged EXE launch and log-based acceptance gate.
- Protects the verified UI3 front-end boot fix from Direct Play regression.
- Verifies the UI3 menu source markers before packaging.
- Ensures the Resonance input mapping remains present.

No `.uasset` or `.umap` is fabricated. Full Pause/Inventory/Map/Quest source integration still requires the live UI3 source tree on AsusRog.

## Hotfix — 2026-10-01
- Fixed invalid PowerShell escaping in the Resonance mapping insertion.
- Fixed gamepad Resonance false-positive: keyboard Key=R is now checked explicitly.
- Prevented automatic deletion of an existing UI4.1 packaged build.
- Propagates nonzero validator exit status to the apply workflow.
- The live AsusRog GameMode currently defaults to gameplay in its normal-launch branch; this conflicts with the previously documented front-end default and remains a separate runtime regression to reconcile before release.
- Remote PowerShell parser execution was not permitted in this session; repository edits were verified by GitHub read-back, not by a fresh packaged test.
