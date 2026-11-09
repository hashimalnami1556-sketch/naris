"""UI-019: prevent copying full save snapshots on every native UMG Tick.

Checks C++ source contracts. A real Unreal 5.7 performance benchmark remains
mandatory before claiming FPS or RAM improvements.
"""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Public/NarisRuntimeSubsystem.h"
MENU=ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSystemMenuWidget.cpp"


class NativeInventoryReadOnlyView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime=RUNTIME.read_text(encoding="utf-8")
        cpp=MENU.read_text(encoding="utf-8")
        cls.tick=cpp.split("void UNarisSystemMenuWidget::NativeTick(",1)[1].split("UTextBlock* UNarisSystemMenuWidget::MakeText(",1)[0]
        cls.menu=cpp.split("void UNarisSystemMenuWidget::RefreshInterface()",1)[1]

    def test_cpp_view_is_const_reference_not_a_copy(self):
        self.assertRegex(self.runtime,r"const\s+FNarisSaveState\s*&\s*GetStateView\(\)\s*const\s*\{\s*return State;\s*\}")

    def test_blueprint_getstate_signature_stays_unchanged(self):
        self.assertRegex(self.runtime,r"UFUNCTION\(BlueprintPure,\s*Category=\"NARIS\|Runtime\"\)\s*FNarisSaveState\s+GetState\(\)\s+const\s*\{\s*return State;\s*\}")

    def test_uses_readonly_live_view_when_runtime_exists(self):
        self.assertIn("if (Runtime)",self.menu)
        self.assertIn("const FNarisSaveState& State = Runtime->GetStateView();",self.menu)
        self.assertNotIn("const FNarisSaveState State = Runtime->GetState();",self.menu)

    def test_inventory_is_still_the_live_actual_save_data(self):
        for field in ("State.InventoryItems[Index]","State.EquippedItems[Index]","State.Currency","State.ActiveQuests.Num()","State.UnlockedWaystones.Num()"):
            self.assertIn(field,self.menu)
        self.assertIn("RefreshInterface();", self.tick)


if __name__=="__main__":
    unittest.main()
