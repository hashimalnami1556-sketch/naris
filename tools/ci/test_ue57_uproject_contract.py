import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[2]/"unreal/NARIS_W04/NARIS_W04.uproject"
class ProjectContract(unittest.TestCase):
 def test_ue57_project_does_not_require_gameplaytags_as_plugin(self):
  d=json.loads(P.read_text(encoding="utf-8"));self.assertEqual(d["EngineAssociation"],"5.7");self.assertNotIn("GameplayTags",{x["Name"] for x in d.get("Plugins",[])})
if __name__=="__main__":unittest.main()
