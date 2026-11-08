"""UI-017 regression: top-center boss bar must not cover right-side objective card.

Source geometry checks only; do not mistake for an Unreal PIE screenshot.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HUD = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"


def rectangles_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def expected_layout(viewport_w, viewport_h, boss_active):
    scale = max(0.75, min(1.6, min(viewport_w / 1920, viewport_h / 1080)))
    safe = 32 * scale
    width = min(410 * scale, viewport_w - 2 * safe)
    height = 112 * scale
    right_x = viewport_w - safe - width
    y = safe
    boss_width = min(viewport_w * 0.6, 790 * scale)
    boss = ((viewport_w - boss_width) / 2, safe + 12 * scale,
            (viewport_w + boss_width) / 2, safe + 110 * scale)
    if boss_active and right_x < boss[2] + 12 * scale:
        y = safe + 122 * scale
    if viewport_w < 720:
        y = max(y, safe + 180 * scale)
    objective = (right_x, y, right_x + width, y + height)
    return objective, boss, safe


class ResponsiveCombatHud(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cpp = HUD.read_text(encoding="utf-8")
        cls.objective = cpp.split("void ANarisHUD::DrawObjectiveCard(", 1)[1].split(
            "void ANarisHUD::DrawInteractionPrompt(", 1
        )[0]
        cls.boss = cpp.split("void ANarisHUD::DrawBossHUD(", 1)[1].split(
            "void ANarisHUD::DrawSubtitle(", 1
        )[0]

    def test_objective_width_fits_safe_viewport(self):
        self.assertIn("Canvas->ClipX - 2.f * Safe", self.objective)

    def test_active_boss_detection_moves_card_only_if_overlap(self):
        self.assertIn("Boss->IsEncounterActive()", self.objective)
        self.assertIn("BossRight", self.objective)
        self.assertIn("Y = Safe + 122.f * Scale;", self.objective)

    def test_narrow_mode_stays_below_player_vitals(self):
        self.assertIn("Canvas->ClipX < 720.f", self.objective)
        self.assertIn("180.f * Scale", self.objective)

    def test_actual_health_and_quest_text_remain(self):
        self.assertIn("Runtime->IsQuestActive", self.objective)
        self.assertIn("Runtime->GetQuestStep", self.objective)
        self.assertIn('DrawGameIcon(TEXT("map")', self.objective)
        self.assertIn("Boss->GetCurrentHealth()", self.boss)

    def test_geometry_never_overlaps_boss_for_supported_reference_sizes(self):
        for resolution in ((1920, 1080), (1280, 720), (1024, 768),
                           (800, 600), (640, 480), (320, 480)):
            objective, boss, safe = expected_layout(*resolution, boss_active=True)
            self.assertFalse(rectangles_overlap(objective, boss), resolution)
            self.assertGreaterEqual(objective[0], safe - 1e-5)
            self.assertLessEqual(objective[2], resolution[0] - safe + 1e-5)

    def test_full_hd_preserves_approved_top_row(self):
        objective, boss, safe = expected_layout(1920, 1080, boss_active=True)
        self.assertEqual(objective[1], safe)
        self.assertFalse(rectangles_overlap(objective, boss))

    def test_short_viewport_with_no_boss_preserves_normal_top_layout(self):
        objective, _boss, safe = expected_layout(1280, 720, boss_active=False)
        self.assertEqual(objective[1], safe)


if __name__ == "__main__":
    unittest.main()
