# NARIS Project Gap Register

This register records missing implementation layers discovered during repository inspection. It distinguishes repository evidence from planned work.

## Confirmed repository state
- `README.md` documents `docs/`, `worlds/`, `data/`, `tools/`, and Unreal as the runtime target.
- The repository currently contains `README.md`, `assets/`, and `docs/` at the top level.
- W04 execution documentation exists under `docs/W04_VERTICAL_SLICE/`.

## Gaps closed in this pass
- W04 world specification added under `worlds/W04_ASHEN_FOREST/`.
- W04 machine-readable registry added under `data/`.
- `tools/` pipeline contract added.
- Bone Beast C++ scaffold implementation added to documentation.

## Remaining implementation gaps
1. A real Unreal `.uproject` and C++ `Source/` tree must exist before code can be compiled in-engine.
2. The scaffold headers currently live in documentation and must be migrated into the Unreal module once the module name is confirmed.
3. Gameplay Tags must be registered in Unreal's project configuration.
4. Animation Montages, Notifies, Niagara Systems, Audio Cues and Widget Blueprints are still engine assets, not repository binaries.
5. Numeric balance values remain TUNE until playtest.
6. Automated CI/build validation for the Unreal project is not yet established.

## Rule
Do not mark an implementation gap as DONE merely because its documentation exists.
