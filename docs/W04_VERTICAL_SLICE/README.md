# CALL OF NARIS — W04 Vertical Slice

## Scope
Ashen Forest → Bone Beast encounter.

## Execution chain
World → Environment → Arena → Boss AI → Combat → Animation → VFX → Audio → UI → Quest → QA.

## Engine target
Unreal Engine 5.x / 60 FPS target. Numeric combat tuning remains `TUNE` until playtest data exists.

## Authoritative design artifacts
- `01_BONE_BEAST_SPEC.md`
- `02_BONE_BEAST_PHASE_TABLE.md`
- `03_BONE_BEAST_AI_STATE_MACHINE.md`
- `04_INTEGRATION_EVENT_MATRIX.md`
- `05_W04_QA_TEST_MATRIX.md`

## Implementation rule
Gameplay state is authoritative. Animation, VFX, Audio and UI react to explicit gameplay events rather than independently deciding boss state.
