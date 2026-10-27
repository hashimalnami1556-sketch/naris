from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[2]
M=json.loads((ROOT/"data/stage32_release_matrix.json").read_text(encoding="utf-8"))
class Stage32ReleaseMatrix(unittest.TestCase):
 def test_fail_closed(self):
  self.assertEqual(M["shipping_policy"],"FAIL_CLOSED")
 def test_required_gates(self):
  ids={g["id"] for g in M["gates"]}
  for x in ("G01_CPP","G02_FINAL_MAP","G03_ANIMBP","G04_MONTAGES","G06_PBR","G08_AUDIO","G09_NIAGARA","G10_GAMEPLAY","G14_EXE"):
   self.assertIn(x,ids)
 def test_no_false_runtime_pass(self):
  for g in M["gates"]:
   self.assertNotEqual(g["status"],"PASS")
if __name__=="__main__": unittest.main()
