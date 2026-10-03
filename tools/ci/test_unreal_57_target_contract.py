import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GAME=ROOT/"unreal"/"NARIS_W04"/"Source"/"NARIS_W04.Target.cs"
EDITOR=ROOT/"unreal"/"NARIS_W04"/"Source"/"NARIS_W04Editor.Target.cs"

class Unreal57TargetContractTests(unittest.TestCase):
    def test_targets_use_ue57_build_settings_and_include_order(self):
        for path in (GAME,EDITOR):
            text=path.read_text(encoding="utf-8")
            self.assertIn("BuildSettingsVersion.V6",text)
            self.assertIn("EngineIncludeOrderVersion.Unreal5_7",text)
            self.assertNotIn("EngineIncludeOrderVersion.Unreal5_4",text)

if __name__=="__main__":
    unittest.main()
