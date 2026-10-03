import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class RewardHudContract(unittest.TestCase):
 def test_hud_draws_timed_reward_toast(self):
  h=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHUD.h").read_text(encoding="utf-8")
  c=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp").read_text(encoding="utf-8")
  self.assertIn("DrawRewardToast",h);self.assertIn("ActiveRewardEventId",h)
  self.assertIn("Rewards->Peek(Event)",c);self.assertIn("4.5f",c);self.assertIn("Rewards->Acknowledge(Event.EventId)",c)
  self.assertIn("ENarisRewardRarity::Legendary",c);self.assertIn("DrawRewardToast(Scale, Safe)",c)
if __name__=="__main__":unittest.main()
