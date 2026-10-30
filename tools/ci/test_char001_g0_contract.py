from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[2]
class Char001G0Contract(unittest.TestCase):
 def test_contract(self):
  d=json.loads((ROOT/"data/char001_skeleton_contract.json").read_text())
  self.assertEqual(d["target_deform_bones"],92)
  self.assertTrue(d["export_policy"]["export_deform_skeleton_only"])
  self.assertFalse(d["export_policy"]["control_rig_exported"])
  self.assertEqual(d["export_policy"]["max_influences_per_vertex"],4)
 def test_twelve_tests_documented(self):
  s=(ROOT/"docs/changes/CHAR-001/CHAR-001-G0-TESTS.md").read_text()
  self.assertEqual(sum(1 for line in s.splitlines() if line[:2] in {f"{i}." for i in range(1,10)} or line[:3] in {"10.","11.","12."}),12)
 def test_auditor_fail_closed(self):
  s=(ROOT/"tools/blender/audit_char001_glb.py").read_text()
  self.assertIn('if not skins: die("no skin")',s)
  self.assertIn('if len(roots)!=1',s)
  self.assertIn('if dups:',s)
if __name__=="__main__": unittest.main()
