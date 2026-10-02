from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisPlayerController.h"
SRC = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
HUD = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"

class NarisUIRuntimeRepairTests(unittest.TestCase):
    def test_controller_cpp_methods_have_header_declarations(self):
        header, source = PUB.read_text(encoding="utf-8"), SRC.read_text(encoding="utf-8")
        implementations = set(re.findall(r'ANarisPlayerController::([A-Za-z_]\w*)\s*\(', source))
        missing = sorted(name for name in implementations if name not in header)
        self.assertEqual(missing, [], f"Missing controller declarations: {missing}")

    def test_frontend_state_is_declared(self):
        header = PUB.read_text(encoding="utf-8")
        for token in ("bFrontEndMenuOpen", "MenuContext", "StartNewGameFromMenu", "ContinueGameFromMenu", "QuitGameFromMenu", "ApplyMenuInputMode"):
            self.assertIn(token, header)

    def test_scrollable_runtime_lists_are_bounded(self):
        hud = HUD.read_text(encoding="utf-8")
        for token in ("State.UnlockedWaystones.Num()", "State.ActiveQuests.Num()", "State.CompletedQuests.Num()", "FMath::Min(State.UnlockedWaystones.Num()", "FMath::Min(State.ActiveQuests.Num()", "FMath::Min(State.CompletedQuests.Num()"):
            self.assertIn(token, hud)

if __name__ == "__main__":
    unittest.main()
