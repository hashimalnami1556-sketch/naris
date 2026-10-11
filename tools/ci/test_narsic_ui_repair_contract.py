from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class NarsicUiRepairContractTests(unittest.TestCase):
    def test_public_runtime_brand_is_narsic(self) -> None:
        engine = read("unreal/NARIS_W04/Config/DefaultEngine.ini")
        project = read("unreal/NARIS_W04/NARIS_W04.uproject")
        controller = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("ProjectName=NARSIC", engine)
        self.assertIn('"Description": "NARSIC W04 Unreal bootstrap project"', project)
        self.assertIn('"PauseMenuTitle", "NARSIC"', controller)
        self.assertNotIn('"PauseMenuTitle", "CALL OF NARIS"', controller)

    def test_mouse_click_path_is_real_and_not_cursor_only(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisPlayerController.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("bool TryHandleMenuMouseClick();", header)
        self.assertIn("Params.Key == EKeys::LeftMouseButton", source)
        self.assertIn("TryHandleMenuMouseClick()", source)
        self.assertIn("GetMousePosition(MouseX, MouseY)", source)
        self.assertIn("SelectedMenuIndex = Index;", source)
        self.assertIn("MenuConfirm();", source)
        self.assertIn("EMouseLockMode::DoNotLock", source)

    def test_tactical_menu_uses_ultrawide_safe_geometry(self) -> None:
        hud = read("unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp")
        style = read("unreal/NARIS_W04/Source/NARIS_W04/Private/NarisUIStyle.cpp")
        self.assertIn("1880.f * Scale", hud)
        self.assertIn("960.f * Scale", hud)
        self.assertIn("Mouse: Click", hud)
        self.assertIn('"NARSIC"', hud)
        self.assertIn("State.ActiveQuests.Num()", hud)
        self.assertIn("State.UnlockedWaystones.Num()", hud)
        self.assertIn("return 32.f * GetViewportScale", style)

    def test_localization_keeps_brand_exact(self) -> None:
        for culture in ("en", "ar"):
            po = read(
                f"unreal/NARIS_W04/Content/Localization/NARIS_Game/{culture}/NARIS_Game.po"
            )
            marker = (
                'msgctxt "NARIS,PauseMenuTitle"\n'
                'msgid "NARSIC"\n'
                'msgstr "NARSIC"'
            )
            self.assertIn(marker, po)


if __name__ == "__main__":
    unittest.main()
