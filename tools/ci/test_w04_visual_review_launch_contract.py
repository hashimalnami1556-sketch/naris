from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "tools/windows/Invoke-NarisW04VisualReview.ps1"
ENGINE = ROOT / "unreal/NARIS_W04/Config/DefaultEngine.ini"
BOOTSTRAP = ROOT / "unreal/NARIS_W04/Content/Python/naris_bootstrap_w04_smoke.py"


class W04VisualReviewLaunchContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.launcher = LAUNCHER.read_text(encoding="utf-8")
        cls.engine = ENGINE.read_text(encoding="utf-8")
        cls.bootstrap = BOOTSTRAP.read_text(encoding="utf-8")

    def test_smoke_scene_is_explicitly_not_the_visual_target(self) -> None:
        self.assertIn('"W04_AshenForest_Blockout"', self.launcher)
        self.assertIn('"W04_AshenForest"', self.launcher)
        self.assertNotIn('"-NarisRuntimeSmoke"', self.launcher)
        self.assertIn('"Do not substitute W04_Prototype.', self.launcher)

    def test_preview_fails_closed_on_missing_or_empty_map(self) -> None:
        self.assertIn('Test-Path -LiteralPath $mapFile', self.launcher)
        self.assertIn('(Get-Item -LiteralPath $mapFile).Length -eq 0', self.launcher)
        self.assertIn('NARIS_VISUAL_PREVIEW_BLOCKED', self.launcher)

    def test_blockout_generation_is_explicit_and_not_shipping(self) -> None:
        self.assertIn('if ($PrepareBlockout)', self.launcher)
        self.assertIn('if ($Map -ne "Blockout")', self.launcher)
        self.assertIn('Invoke-NarisW04ProductionBlockout.ps1', self.launcher)
        self.assertIn('Production map file existence is NOT shipping approval', self.launcher)

    def test_existing_ci_smoke_bootstrap_kept_intact(self) -> None:
        self.assertIn('GameDefaultMap=/Game/NARIS/W04/Maps/W04_Prototype', self.engine)
        self.assertIn('MAP_PATH = "/Game/NARIS/W04/Maps/W04_Prototype"', self.bootstrap)
        self.assertIn('DEV_SmokeFloor', self.bootstrap)
        self.assertIn('SMOKE ONLY', self.launcher)

    def test_inspection_does_not_launch_unreal(self) -> None:
        inspect = self.launcher.index('if ($InspectOnly)')
        spawn = self.launcher.index('Start-Process')
        self.assertLess(inspect, spawn)
        self.assertIn('NARIS_VISUAL_PREVIEW_INSPECT_PASS', self.launcher)


if __name__ == "__main__":
    unittest.main()
