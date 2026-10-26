from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
class ShippingLauncherTests(unittest.TestCase):
 def test_wrapper_uses_canonical_gates_not_a_missing_commandlet(self):
  source=(ROOT/'tools/windows/Build-NarisWindows.ps1').read_text()
  self.assertNotIn('-run=NarisValidateShippingMap',source)
  self.assertIn('Invoke-NarisWindowsReleaseCandidate.ps1',source)
  self.assertIn('Invoke-NarisWindowsPackage.ps1',source)
 def test_old_archive_cannot_satisfy_new_build(self):
  source=(ROOT/'tools/windows/Build-NarisWindows.ps1').read_text()
  self.assertIn('[Guid]::NewGuid()',source)
  rc=(ROOT/'tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1').read_text()
  self.assertIn('Archive directory is not empty',rc)
  self.assertIn('Move-Item -LiteralPath $OldReport',rc)
  self.assertIn('executable_sha256',rc)
 def test_promotion_validates_before_copying(self):
  source=(ROOT/'unreal/NARIS_W04/Content/Python/naris_stage8_promote_final_map.py').read_text()
  self.assertLess(source.index('evaluate_snapshot(requirements'),source.index('eal.duplicate_asset'))
  self.assertLess(source.index("if report['errors']"),source.index('eal.duplicate_asset'))
  self.assertNotIn('set_actor_label',source)
 def test_shipping_reports_do_not_claim_playtest(self):
  source=(ROOT/'tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1').read_text()
  self.assertIn('runtime_validation_status = "not_run"',source)
  self.assertIn('release_approved = $false',source)
if __name__=='__main__':unittest.main()
