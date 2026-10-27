from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
A=(ROOT/"unreal/NARIS_W04/Content/Python/naris_stage33_bind_animation.py").read_text()
P=(ROOT/"unreal/NARIS_W04/Content/Python/naris_stage33_bind_pbr_textures.py").read_text()
R=(ROOT/"tools/windows/Invoke-NarisStage33BindAssets.ps1").read_text()
class Stage33(unittest.TestCase):
 def test_animation_is_not_fabricated(self):
  self.assertIn("never fabricates animation content",A)
  self.assertIn("ANIMATION_BLUEPRINT",A)
  for x in ("AM_Hero_LightAttack","AM_Hero_HeavyAttack","AM_Hero_Dodge","AM_Hero_Parry"): self.assertIn(x,A)
 def test_pbr_channels(self):
  for x in ("BaseColor","Normal","Roughness","Metallic","AO","Height"): self.assertIn(x,P)
  self.assertIn("no placeholder textures are created",P)
 def test_order(self):
  self.assertLess(R.index("naris_author_material_instances.py"),R.index("naris_stage33_bind_pbr_textures.py"))
  self.assertLess(R.index("naris_stage33_bind_animation.py"),R.index("naris_stage30_validate_runtime_assets.py"))
if __name__=="__main__": unittest.main()
