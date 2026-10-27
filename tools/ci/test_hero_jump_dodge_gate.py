from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
INI=(ROOT/"unreal/NARIS_W04/Config/DefaultInput.ini").read_text(encoding="utf-8")
CPP=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp").read_text(encoding="utf-8")
class HeroInputGate(unittest.TestCase):
 def test_jump_and_dodge_do_not_share_space(self):
  self.assertIn('ActionName="Jump",Key=(KeyName="SpaceBar")',INI)
  self.assertIn('ActionName="Dodge",Key=(KeyName="LeftControl")',INI)
  self.assertNotIn('ActionName="Dodge",Key=(KeyName="SpaceBar")',INI)
 def test_character_binds_jump(self):
  self.assertIn('BindAction(TEXT("Jump"), IE_Pressed',CPP)
  self.assertIn('BindAction(TEXT("Jump"), IE_Released',CPP)
 def test_jump_tuning_present(self):
  for x in ("JumpZVelocity","AirControl","GravityScale"): self.assertIn(x,CPP)
if __name__=="__main__": unittest.main()
