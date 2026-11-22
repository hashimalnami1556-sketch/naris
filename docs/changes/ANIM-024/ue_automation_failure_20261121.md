# ANIM-024 — Real W04 Project.* Automation failure / input-config blocker (2026-11-21)

**Result: FAILED.** Actual Windows Unreal Engine 5.7.4 commandlet launched against **local, uncommitted** W04 project checkout `C:\dev\NARIS_ENV020_20261114\unreal\NARIS_W04`. No Unreal production asset or input configuration was edited during this test.

## Actual execution

- Binary: `UnrealEditor-Cmd.exe`; flags: `-unattended -nop4 -nullrhi -nosplash -NoSound "-ExecCmds=Automation RunTests Project.; Quit" "-TestExit=Automation Test Queue Empty"`.
- Test executed: `Project.Maps.PIE` on `/Game/NARIS/W04/Maps/W04_Prototype`.
- Unreal report: **succeeded=0, failed=1, notRun=0, errors=9**, `Test Completed. Result={Fail}`, nonzero process exit **1**. Raw engine log additionally prints automation commandlet `EXIT CODE: -1`. These values are distinct layers of reporting.
- Actual JSON report: `C:\dev\NARIS_ANIM024_20261121\automation_reports\index.json` SHA256 `2D0541E69F975D248FDAEC95E6E06A034B631526575F7CA23BBF43127AF216C8`.
- Actual engine log: `C:\dev\NARIS_ANIM024_20261121\automation_editor.log` SHA256 `D9B4D9F8F7F8166230D53EA54D5BE0EA5A52D362B565B0E4A0F5310AA66BB947`.
- HTML report: `C:\dev\NARIS_ANIM024_20261121\automation_reports\index.html`.

## Reproduced failures

1. Nine `LogInput: Error: Duplicate mapping of key ( for axis ...` errors: `MoveForward` twice, `MoveRight` twice, `LookYaw` once, `LookPitch` once, `SwimVertical` three times.
2. Six missing UI icon references: `/Game/NARIS/UI/Icons/{health,energy,mana,attack,defense,map}`.
3. `W04_Prototype.umap` warning: missing script import `/Script/AugmentedReality`.
4. Separate startup warning: absent `Content/Localization/NARIS_Game/NARIS_Game.locmeta`.

The nine **input errors**, not merely the warnings, correspond to the test's reported error count. The map loaded and `MapCheck` had zero map-check errors before the PIE failure.

## Root cause supported by actual inspected files

- Local `Config/DefaultInput.ini` contains many serialized `+ActionMappings=(...,Key=()` and `+AxisMappings=(...,Key=()` entries with the key name missing. These entries are not valid playable bindings. This directly explains why UE sees multiple mappings of an effectively invalid key `(`.
- GitHub `unreal/NARIS_W04/Config/DefaultInput.ini` on ANIM-024 branch contains **57** `Key=(KeyName="...")` entries instead of the conventional serialized scalar `Key=SpaceBar`, `Key=W` etc. It also contains **one literal backslash-n** between mappings. This is a **probable source of corruption**. Causation requires an isolated file-shape correction and a new Unreal automation run, not an assumption.
- Source intent provides **43 Action** and **14 Axis** mappings. Correct keys can be recovered from the source without inventing controls.
- Proposed trial (ISOLATED COPY ONLY): normalize the one escaped newline and replace `Key=(KeyName="X")` with `Key=X`. Never do broad replacement on the existing local original or force-clean untracked art.

## Release gate and sequencing

- **Stop**: ANIM-024 target authoring/IK Retargeter/Gameplay approval remains blocked.
- Repair automation/input configuration in a **new isolated review copy** and rerun `Project.*` tests before applying production code changes.
- Separately review UI icon asset references, map AugmentedReality import and localization metadata; do not paper over errors by ignoring them.
- Required remaining tests: Development Build, BuildCookRun, actual animation montage playback, dedicated server plus two clients, fixed-seed 1920x1080 before/after/diff, FPS/RAM. **NOT RUN**.
- **Rollback**: no original project content has been changed. Revert this documentation update if needed and delete only isolated trial copy after QA review.

References: [Epic user input documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-user-inputs-in-unreal-engine), [UE Input mapping serialization example](https://github.com/alivojdanian/UnrealEngineAI/blob/master/Config/DefaultInput.ini).
