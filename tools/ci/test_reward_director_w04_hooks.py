import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class RewardHooks(unittest.TestCase):
 def test_memory_crystal_queues_exploration_presentation(self):
  s=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisMemoryCrystal.cpp").read_text(encoding="utf-8")
  self.assertIn("UNarisRewardDirectorSubsystem",s);self.assertIn("ENarisRewardKind::Exploration",s);self.assertIn("memory_crystal_01",s)
 def test_bone_beast_queues_boss_presentation_after_completion(self):
  s=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp").read_text(encoding="utf-8")
  self.assertIn("UNarisRewardDirectorSubsystem",s);self.assertIn("ENarisRewardKind::Boss",s);self.assertIn("bone_beast",s)
  self.assertLess(s.index("bEncounterComplete = true;",s.index("void ABoneBeastBoss::CompleteEncounter")),s.index("Rewards->Enqueue(Event);"))
if __name__=="__main__":unittest.main()
