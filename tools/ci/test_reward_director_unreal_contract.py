import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
H=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Public/NarisRewardDirectorSubsystem.h"
CPP=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRewardDirectorSubsystem.cpp"
TEST=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/Tests/NarisRewardDirectorTests.cpp"
class RewardDirectorUnrealContract(unittest.TestCase):
 def test_subsystem_and_blueprint_contract_exist(self):
  h=H.read_text(encoding="utf-8");self.assertIn("UGameInstanceSubsystem",h);self.assertIn("UFUNCTION(BlueprintCallable) bool Enqueue",h);self.assertIn("FNarisRewardQueued",h)
 def test_priority_and_ack_implementation_exist(self):
  c=CPP.read_text(encoding="utf-8");self.assertIn("Legendary",c);self.assertIn("Priority",c);self.assertIn("Acknowledge",c);self.assertIn("bAcked=true",c)
 def test_native_automation_covers_priority_and_replay(self):
  t=TEST.read_text(encoding="utf-8");self.assertIn("LegendaryPreemptsStandard",t);self.assertIn("RejectsMismatchedReplay",t)
if __name__=="__main__":unittest.main()