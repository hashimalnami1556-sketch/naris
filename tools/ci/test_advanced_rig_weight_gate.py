from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"tools/blender/naris_advanced_rig_weight_gate.py"
S=P.read_text(encoding="utf-8")
class AdvancedRigGateContract(unittest.TestCase):
 def test_targets(self):
  for n in ("92","82","106","78","146"): self.assertIn(n,S)
 def test_weight_rules(self):
  self.assertIn("MAX_INFLUENCES=4",S)
  self.assertIn("unweighted_count",S)
  self.assertIn("lr_bleed_suspect_count",S)
 def test_visual_gate_never_auto_passes(self):
  self.assertIn('"visual_deformation_gate":"PENDING_ARTIST_REVIEW"',S)
  self.assertIn('"production_candidate":False',S)
if __name__=="__main__": unittest.main()
