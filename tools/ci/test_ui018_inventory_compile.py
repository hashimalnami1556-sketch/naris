"""UI-018: regression tests for real C++ Inventory page compile blocker.

Unreal C++ build cannot run on Linux CI; these scope tests ensure the
Inventory flag is declared before use and uses the actual enum state.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MENU_CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSystemMenuWidget.cpp"
GAMEPLAY_TYPES = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"


class InventoryMenuCompileContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = MENU_CPP.read_text(encoding="utf-8").split(
            "void UNarisSystemMenuWidget::RefreshInterface()", 1
        )[1]
        cls.state = GAMEPLAY_TYPES.read_text(encoding="utf-8")

    def test_inventory_flag_is_declared_before_first_use(self):
        declaration = re.search(
            r"\bconst\s+bool\s+bInventoryPage\s*=\s*"
            r"Controller->GetPauseMenuPage\(\)\s*==\s*"
            r"ENarisPauseMenuPage::Inventory\s*;", self.body
        )
        self.assertIsNotNone(declaration, "bInventoryPage must have a C++ definition")
        self.assertLess(declaration.end(), self.body.index("if (bInventoryPage)"))

    def test_flag_is_in_scope_for_title_as_well_as_content(self):
        declared = re.search(r"\bconst\s+bool\s+bInventoryPage\s*=", self.body)
        self.assertIsNotNone(declared)
        self.assertEqual(self.body.count("const bool bInventoryPage"), 1)
        self.assertIn("StatusTitleText->SetText(", self.body)
        self.assertGreater(self.body.index("StatusTitleText->SetText("), declared.start())

    def test_inventory_fields_exist_in_actual_gameplay_save_schema(self):
        for field in ("InventoryItems", "EquippedItems", "Currency"):
            with self.subTest(field=field):
                self.assertIn(field, self.state)
                self.assertIn("State." + field, self.body)

    def test_normal_menu_and_click_handlers_remain(self):
        text = MENU_CPP.read_text(encoding="utf-8")
        self.assertIn("Controller->ActivateMenuIndex(MenuIndex)", text)
        self.assertIn("Controller->SelectMenuIndex(MenuIndex)", text)
        self.assertIn("State.UnlockedWaystones.Num()", self.body)


if __name__ == "__main__":
    unittest.main()
