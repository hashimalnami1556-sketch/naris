# NARIS UI4.1 / Runtime sync — 2026-10-01

## Verified predecessor evidence
The local Unreal project produced a packaged Windows Development build and was launched as a standalone EXE. The runtime log confirmed:
- `NARIS_FRONTEND READY`
- `NARIS_RUNTIME_READY`
- the automatic Direct Play path was identified as the reason the menu could be bypassed and was corrected so Direct Play requires an explicit `NarisDirectPlay` flag.

## UI4.1 repository payload
`NARIS_MASTER/14_UI_UX/releases/UI4_1/` contains:
- guarded Apply script;
- packaged-build log validator;
- rollback script;
- acceptance criteria;
- changelog.

The installer validates expected UI3 source markers and refuses to guess when the source differs.

## Scope not yet claimed
- UI4.1 has not been re-applied on AsusRog after this repository sync because the remote host is offline.
- Full Pause / Inventory / Map / Quest source integration is not represented as complete.
- No `.uasset` or `.umap` is fabricated by this repository sync.
- The UI4.1 local workflow targets UE 5.7, but this update does not silently rewrite the repository's canonical engine descriptor.

## Godot status
The audited Godot runtime archive contains 34 non-empty files, but it remains a runtime skeleton rather than a master build. Missing production evidence includes actual Autoload wiring, playable scene actors, real combat hit detection, production assets/audio, production-grade HUD and reliable input packaging.

## Next execution gate
When AsusRog returns online:
1. sync/pull main;
2. run `Apply-UI4_1.ps1`;
3. require `NARIS_UI4_1_GATE PASS`;
4. integrate the remaining in-game shell screens against the live source;
5. build a fresh Windows package and attach logs as engine evidence.
