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

## AsusRog source hotfix verification — 2026-10-01
- Restored default Front-End path in local `NarisGameModeBase.cpp`: normal launch sets `bGameStarted=false`, pauses play, enables mouse cursor and uses `FInputModeGameAndUI`; direct gameplay remains opt-in for smoke/direct-play flags.
- Unreal Engine 5.7 `NARISEditor Win64 Development` compile completed successfully (`Result: Succeeded`, exit code 0) following local source edit.
- Packaged Windows UI4.1 and interactive mouse-click validation were not rerun in this pass; do not conflate successful Editor compile with packaged acceptance.

## 2026-10-02 — front-end input regression
- On AsusRog, corrected `ANarisPlayerCharacter::TogglePause`: Esc/Start while the game has not started no longer calls `GM->StartGame()` and bypasses the main menu.
- Unreal Engine 5.7 NARISEditor Win64 Development compilation completed successfully (`Result: Succeeded`, exit 0).
- Windows Development `WindowsDevelopment_UI4_2` packaging was initiated, but this entry does not claim packaging/runtime validation until an explicit completion result is recorded.
- The corrected C++ file is currently in `C:\Users\Admin\NARIS\Source\NarisCore\Private\NarisPlayerCharacter.cpp`; reconcile with canonical GitHub runtime code before claiming repository-source synchronization.
