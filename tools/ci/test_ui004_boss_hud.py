"""Contract test for UI-004's boss encounter placement.
This is static source validation; Unreal runtime tests are mandatory before merge.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
HUD = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"


class BossHudPlacement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = HUD.read_text(encoding="utf-8")
        cls.segment = raw.split("void ANarisHUD::DrawBossHUD(", 1)[1].split(
            "void ANarisHUD::DrawSubtitle(", 1
        )[0]

    def test_boss_bar_is_top_center_not_bottom(self):
        self.assertIn("const float Y = Safe + 12.f * Scale;", self.segment)
        self.assertIn("const float X = (Canvas->ClipX - W) * 0.5f;", self.segment)
        self.assertNotIn("const float Y = Canvas->ClipY - Safe - H;", self.segment)

    def test_boss_bar_uses_actual_gameplay_health(self):
        self.assertIn("Boss->GetCurrentHealth()", self.segment)
        self.assertIn("Boss->GetConfiguredMaxHealth()", self.segment)
        self.assertIn("Boss->IsEncounterActive()", self.segment)

    def test_boss_bar_uses_actual_phase(self):
        self.assertIn("Boss->GetPhase()", self.segment)
        self.assertIn("ENarisBossPhase::Phase3", self.segment)

    def test_boss_health_is_bounded(self):
        self.assertIn("FMath::Min(Canvas->ClipX * 0.60f, 790.f * Scale)", self.segment)
        self.assertIn("FNarisUIStyle::SafeRatio(HP, MaxHP)", self.segment)


if __name__ == "__main__":
    unittest.main()
