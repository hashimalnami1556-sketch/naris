"""Static regression guard: approved W04 front-end is right-aligned, pause menu is unchanged.

Not a substitute for Unreal UMG/PIE tests.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSystemMenuWidget.cpp"


class MainMenuLayoutContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = SOURCE.read_text(encoding="utf-8")
        cls.front = cls.cpp.split("void UNarisSystemMenuWidget::RefreshInterface()", 1)[1]

    def test_front_end_uses_approved_right_side(self):
        self.assertIn("FAnchors(0.71f, 0.27f, 0.95f, 0.83f)", self.front)
        self.assertNotIn("FAnchors(0.06f, 0.24f, 0.42f, 0.81f)", self.front)

    def test_other_menu_keeps_original_layout(self):
        self.assertIn("FAnchors(0.035f, 0.155f, 0.605f, 0.90f)", self.front)

    def test_live_native_button_handlers_remain(self):
        self.assertIn("Controller->ActivateMenuIndex(MenuIndex)", self.cpp)
        self.assertIn("Controller->SelectMenuIndex(MenuIndex)", self.cpp)

    def test_front_end_backdrop_leaves_scene_visible(self):
        self.assertIn("FLinearColor(0.004f, 0.005f, 0.007f, 0.22f)", self.front)


if __name__ == "__main__":
    unittest.main()
