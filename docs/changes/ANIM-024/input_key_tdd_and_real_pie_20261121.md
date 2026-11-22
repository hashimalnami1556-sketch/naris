# ANIM-024 — W04 input binding repaired in source and verified with real Unreal PIE (2026-11-21)

**Status:** W04 `DefaultInput.ini` mapping serialization source defect is fixed on **draft** PR #110. This does NOT certify overall ANIM-024, live gameplay, network, IK Retargeter or release.

## Actual reproducible failure (baseline)

- The local original W04 checkout: `C:\dev\NARIS_ENV020_20261114\unreal\NARIS_W04`. Connected AsusRog, actual Unreal 5.7.4 commandlet.
- `Project.Maps.PIE` against `W04_Prototype` returned **1 failed / 0 passed, 9 errors** from `LogInput: Error: Duplicate mapping of key ( for axis ...`, exit code **1**; `automation_editor.log`, SHA256 `D9B4D9F8F7F8166230D53EA54D5BE0EA5A52D362B565B0E4A0F5310AA66BB947`, `automation_reports/index.json`, SHA256 `2D0541E69F975D248FDAEC95E6E06A034B631526575F7CA23BBF43127AF216C8`.
- Local original `DefaultInput.ini` was observed with **56** `Key=()` physical lines and no valid scalar action or axis keys. The raw GitHub source file had **57** `Key=(KeyName="...")` encoded keys and **one literal backslash-n** joining two action mappings.
- **Caveat:** Original checkout config file mtime was observed at 01:58:30 after the original automation process. No pre-run byte hash was retained, so no byte-preservation claim is made for that original `.ini` even though the test script itself did not explicitly write it. Existing untracked production assets must not be cleaned, added in bulk or overwritten.

## Safe isolated test: source recovery, real PIE after

- Copied 253 Content files (~140.41 MB), binaries/config/source to `C:\dev\NARIS_ANIM024_20261121\InputReviewProject`, excluding DerivedDataCache, Saved and Intermediate, using Robocopy **exit 1 (successful file copy)**.
- Modified **only this isolated copy's** `Config/DefaultInput.ini` to replace each `Key=(KeyName="X")` with Unreal-compatible `Key=X` and restore one real newline. Preserved **43 action mappings and 14 axis mappings**; zero `Key=()`.
- Re-ran the SAME engine 5.7.4 automation command with `-ExecCmds="Automation RunTests Project.; Quit"`, `-TestExit="Automation Test Queue Empty"`, `-unattended -nop4 -nullrhi -nosplash -NoSound`, against isolated project's `W04_Prototype`.
- **Actual AFTER:** one `Project.Maps.PIE` test **Success with warnings**, **0 errors, 13 warnings**, engine commandlet process exit **0** and `TEST COMPLETE. EXIT CODE: 0`.
- Evidence `C:\dev\NARIS_ANIM024_20261121\input_fix_reports\index.json` SHA256 `A76F74D430B30FCB6DDEC1B429C5A7607C1CAE8EA8180308BE371073FFEC573B`; `input_fix_automation.log` SHA256 `92D2EA53FD2E194C67AD79F6E3681090BAF89AD524B4DF61ACAD6834A1F76CC7`. HTML report at `input_fix_reports\index.html`.
- Remaining 13 warnings include the known missing six UI icons and missing `/Script/AugmentedReality` import; do not silently dismiss them. The fix did not address those unrelated issues.

## GitHub TDD proof and source fix

1. New `tests/anim024/test_anim024_input_config.py` RED commit `c77cf95`, [failing run 44853722695](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44853722695), reproducing malformed `Key=(KeyName=...)` and line joining.
2. `unreal/NARIS_W04/Config/DefaultInput.ini` corrected by `5d7fd7b`. A first intermediate test run [44853773342](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44853773342) still failed due to a **test-regex syntax bug**, not an Unreal mapping failure. Fixed the test without weakening the scalar-key assertion in `41e5cbe`.
3. [GREEN run 44853845818](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44853845818): **73 tests discovered, 71 passed, 2 user GLB integration tests skipped**. [NARIS Unreal Validate 44853845866](https://github.com/hashimalnami1556-sketch/naris/actions/runs/44853845866) also passed. Neither GitHub workflow includes local UE playback; actual local PIE above is separate evidence.
4. Nothing was merged; PR #110 remains DRAFT. This is a prerequisite config correction inside the current change, not a declaration of completed ANIM-024.

## Remaining gates

- Real 87-bone production hero not verified; only a local 53-bone Ashen Vessel. Local wolf V8/V9 each 35 bones share Skeleton; four local Montages work as loadable objects but actual gameplay, notifies classes, montage slot execution and replication unproven.
- Exact ten W04 manifest Montage paths still fail to load in the local checkout; do NOT fabricate substitutes or silently remap the roles.
- Development Build, BuildCookRun, dedicated server + two clients, measured FPS/RAM and 1920×1080 paired engine screenshots/diff are separate outstanding checks. Build may be attempted in isolated project and its result must be logged before claiming pass.
- **Rollback** of input source fix: revert `5d7fd7b` with relevant tests/docs on draft branch; isolated review copy can be deleted only after evidentiary handoff. Original untracked local assets are preserved.

Official sources: [Epic UE5 Input](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-user-inputs-in-unreal-engine), [Epic Python 5.7 API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/?application_version=5.7).
