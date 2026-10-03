from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisDailyNPC.h"
PRIVATE = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisDailyNPC.cpp"

class DailyNPCRuntimeContract(unittest.TestCase):
    def test_npc_actor_exposes_runtime_routine_and_interaction(self):
        h = PUBLIC.read_text(encoding="utf-8")
        for token in ("class NARIS_W04_API ANarisDailyNPC", "FName NPCId", "FNarisNPCScheduleEntry", "SetWorldHour", "SetStormActive", "InteractNPC", "GetCurrentActivity"):
            self.assertIn(token,h)

    def test_schedule_is_deterministic_and_handles_midnight(self):
        cpp=PRIVATE.read_text(encoding="utf-8")
        for token in ("FMath::Fmod", "EndHour < StartHour", "WorldHour >= StartHour || WorldHour < EndHour", "FMath::Clamp", "FMath::IsFinite"):
            self.assertIn(token,cpp)

    def test_dialogue_quest_is_not_auto_completed(self):
        cpp=PRIVATE.read_text(encoding="utf-8")
        self.assertIn("Runtime->StartQuest(QuestToOffer.ToString()",cpp)
        self.assertNotIn("Runtime->CompleteQuest(",cpp)
        self.assertIn("bQuestOffered",cpp)

    def test_npc_does_not_tick_every_frame(self):
        cpp=PRIVATE.read_text(encoding="utf-8")
        self.assertIn("PrimaryActorTick.bCanEverTick = false",cpp)
        self.assertIn("SetTimer(",cpp)

if __name__=="__main__":
    unittest.main()
