from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisEnvironmentQuestTrigger.h"
CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisEnvironmentQuestTrigger.cpp"

class EnvironmentQuestTriggerContract(unittest.TestCase):
    def test_trigger_exposes_environment_types_and_persistence(self):
        h=H.read_text(encoding="utf-8")
        for token in ("ENarisEnvironmentTriggerType","RegionEnter","CaveEnter","MountainPeak","WaterEnter","BossArena","bOneTime","TriggerId","TargetId","RequiredQuest","QuestToStart","QuestStepToSet"):
            self.assertIn(token,h)

    def test_trigger_checks_player_and_requirements(self):
        cpp=CPP.read_text(encoding="utf-8")
        for token in ("IsPlayerControlled()","IsQuestActive","HasNarrativeTriggered","TriggerNarrative"):
            self.assertIn(token,cpp)

    def test_trigger_can_start_or_advance_quest(self):
        cpp=CPP.read_text(encoding="utf-8")
        self.assertIn("Runtime->StartQuest",cpp)
        self.assertIn("Runtime->SetQuestStep",cpp)

    def test_one_time_trigger_is_persisted_and_autosaved(self):
        cpp=CPP.read_text(encoding="utf-8")
        for token in ("Runtime->TriggerNarrative", "Runtime->SaveState(Runtime->DefaultAutoSaveSlot)"):
            self.assertIn(token,cpp)

if __name__=="__main__":
    unittest.main()
