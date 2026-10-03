import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class CameraContract(unittest.TestCase):
 def test_ue57_engine_cameras_dependency(self):
  b=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.Build.cs").read_text(encoding="utf-8");self.assertIn('"EngineCameras"',b)
  d=json.loads((ROOT/"unreal/NARIS_W04/NARIS_W04.uproject").read_text(encoding="utf-8"));self.assertIn("EngineCameras",{p["Name"] for p in d["Plugins"] if p.get("Enabled")})
if __name__=="__main__":unittest.main()
