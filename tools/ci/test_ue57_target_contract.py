import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"unreal/NARIS_W04/Source"
class UE57TargetContract(unittest.TestCase):
 def test_targets_use_ue57_build_contract(self):
  for name in ("NARIS_W04.Target.cs","NARIS_W04Editor.Target.cs"):
   s=(ROOT/name).read_text(encoding="utf-8");self.assertIn("BuildSettingsVersion.V6",s,name);self.assertIn("EngineIncludeOrderVersion.Unreal5_7",s,name)
if __name__=="__main__":unittest.main()
