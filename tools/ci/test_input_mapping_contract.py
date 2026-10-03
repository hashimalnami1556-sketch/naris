import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[2]/"unreal/NARIS_W04/Config/DefaultInput.ini"
class InputMappingContract(unittest.TestCase):
 def test_no_empty_legacy_keys_and_core_controls_exist(self):
  s=P.read_text(encoding="utf-8");self.assertNotIn("Key=()",s)
  for token in ('ActionName="LightAttack"','Key=LeftMouseButton','ActionName="Dodge"','Key=SpaceBar','ActionName="Interact"','Key=E','ActionName="Pause"','Key=Escape','AxisName="MoveForward"','Key=W','AxisName="MoveRight"','Key=D','AxisName="LookYaw"','Key=MouseX'): self.assertIn(token,s)
if __name__=="__main__":unittest.main()
