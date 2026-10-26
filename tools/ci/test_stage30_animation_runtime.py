from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
H=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHeroCharacter.h").read_text(encoding="utf-8")
C=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp").read_text(encoding="utf-8")
B=(ROOT/"unreal/NARIS_W04/Content/NARIS/W04/Animation/W04_AnimationBindings.json").read_text(encoding="utf-8")
class Stage30AnimationRuntime(unittest.TestCase):
 def test_smoke_attack_not_production_default(self):
  self.assertIn("bImmediateSmokeAttackHit = false",H)
 def test_dodge_requires_animation_start(self):
  self.assertIn("bool OnDodgeRequested()",H)
  self.assertIn("bDodgeAnimationStarted = OnDodgeRequested()",C)
  self.assertLess(C.index("bDodgeAnimationStarted = OnDodgeRequested()"),C.index("Energy->Spend(DodgeEnergyCost)"))
 def test_expected_montages_registered(self):
  for x in ("AM_Hero_LightAttack","AM_Hero_HeavyAttack","AM_Hero_Dodge"):
   self.assertIn(x,B)
if __name__=="__main__": unittest.main()
