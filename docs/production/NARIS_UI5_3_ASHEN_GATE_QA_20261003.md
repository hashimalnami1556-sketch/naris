# CALL OF NARIS — UI5.3 Gate Quest, Visual Route, QA
Date: 2026-10-03
Project: C:\Users\Admin\NARIS
Engine: UE 5.7.4 (Win64 Development)

## Changes actually implemented
- New UCLASS ANarisAshGateActor, editor-placeable quest barrier.
- Gate is sealed while AshenGateOpened is false; it disables collision when the Gate Warden is defeated.
- Crossing the far side of the gate sets AshenGateEntered, unlocks and selects BellMarsh in chapter state, attempts NARIS_Autosave during normal play.
- NarisGateCrossSmoke simulates crossing without writing autosave, preserving user save slots.
- Quest HUD shows gate distance / SEALED-OPEN and chapter progression.
- L_AshenGate_QuestPlayable_V9: repositioned 44 prior gateway elements beyond boss, added 13 walkway meshes, 16 basalt spires, 10 cairns, 3 root arches; replaced portal's physical collision with quest barrier.
- V8 remains available as previous working map.

## Real verification
- Unreal Editor build of gate UCLASS succeeded.
- WindowsDevelopment_UI5_3_AshenGate build / cook / stage / pak / archive: BUILD SUCCESSFUL, exit 0.
- WindowsDevelopment_UI5_3_1_GateQA build / cook / stage / pak / archive: BUILD SUCCESSFUL, exit 0.
- Packaged smoke test with -NarisQuestSmoke -NarisGateCrossSmoke:
  NARIS_RELEASE_GATE PASS
  NARIS_RUNTIME_READY
  NARIS_QUEST_SMOKE PASS
  NARIS_ASH_GATE_ACTIVE
  NARIS_ASH_GATE_OPEN PassageEnabled=1
  NARIS_ASH_GATE_ENTERED ChapterOK=1 Autosave=0 Smoke=1
- Autosave=0 is intentional only in simulated crossing, not proof of failed normal autosave.

## Remaining acceptance
- User-driven WASD navigation, physical collision and real-world crossing through gate require direct interactive QA.
- Bell Marsh scene itself remains to be built; chapter state unlock is not equivalent to entering a finished second map.
- More detailed environment art, polished portraits, character group system, retargeted animations, profiling and shipping tests remain.
