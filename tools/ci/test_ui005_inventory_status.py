"""Static contract for UI-005 inventory data wiring.

Unreal build/PIE and Arabic localization checks must still run before merge.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MENU = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSystemMenuWidget.cpp"


class InventoryStatusContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = MENU.read_text(encoding="utf-8")
        cls.body = cls.cpp.split("void UNarisSystemMenuWidget::RefreshInterface()", 1)[1]

    def test_inventory_page_condition(self):
        self.assertIn("ENarisPauseMenuPage::Inventory", self.body)
        self.assertIn("if (bInventoryPage)", self.body)

    def test_data_is_live_not_mocked(self):
        self.assertIn("Runtime->GetState()", self.body)
        self.assertIn("State.EquippedItems[Index]", self.body)
        self.assertIn("State.InventoryItems[Index]", self.body)
        self.assertIn("State.Currency", self.body)

    def test_bounded_rows(self):
        self.assertIn("FMath::Min(State.EquippedItems.Num(), 5)", self.body)
        self.assertIn("FMath::Min(State.InventoryItems.Num(), 7)", self.body)

    def test_empty_stores_use_localizable_placeholders(self):
        self.assertIn('NSLOCTEXT("NARIS", "UMGNoEquipment"', self.body)
        self.assertIn('NSLOCTEXT("NARIS", "UMGNoInventory"', self.body)

    def test_normal_status_remains(self):
        self.assertIn("State.UnlockedWaystones.Num()", self.body)
        self.assertIn("State.ActiveQuests.Num()", self.body)

    def test_buttons_still_use_native_handlers(self):
        self.assertIn("Controller->ActivateMenuIndex(MenuIndex)", self.cpp)
        self.assertIn("Controller->SelectMenuIndex(MenuIndex)", self.cpp)


if __name__ == "__main__":
    unittest.main()
