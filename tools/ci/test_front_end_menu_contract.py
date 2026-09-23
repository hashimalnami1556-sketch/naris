from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class FrontEndMenuContractTests(unittest.TestCase):
    def test_normal_session_opens_front_end_but_runtime_smoke_bypasses_it(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn('FParse::Param(FCommandLine::Get(), TEXT("NarisRuntimeSmoke"))', source)
        self.assertIn('FParse::Param(FCommandLine::Get(), TEXT("NarisSkipFrontEnd"))', source)
        self.assertIn("Runtime->ConsumeFrontEndBypassOnce()", source)
        self.assertIn("OpenFrontEndMenu()", source)

    def test_front_end_and_pause_have_distinct_main_menu_sizes(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("constexpr int32 PauseMainMenuCount = 3", source)
        self.assertIn("constexpr int32 FrontEndMainMenuCount = 5", source)
        self.assertIn("ENarisMenuContext::FrontEnd", source)
        self.assertIn("ENarisMenuContext::Pause", source)

    def test_front_end_exposes_new_continue_settings_controls_quit(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        for key in (
            "FrontEndNewGame",
            "FrontEndContinue",
            "PauseSettings",
            "PauseControls",
            "FrontEndQuit",
        ):
            self.assertIn(key, source)

    def test_continue_requires_real_auto_save(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("bool ANarisPlayerController::CanContinueGame() const", source)
        self.assertIn("UGameplayStatics::DoesSaveGameExist", source)
        self.assertIn("Runtime->DefaultAutoSaveSlot", source)
        self.assertIn("FrontEndNoSave", source)
        self.assertIn("if (!CanContinueGame())", source)

    def test_new_game_resets_saves_then_reloads_world_once(self) -> None:
        controller = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        runtime_h = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisRuntimeSubsystem.h"
        )
        runtime_cpp = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        for token in (
            "Runtime->BeginNewGame()",
            "Runtime->SaveState(Runtime->DefaultAutoSaveSlot)",
            "Runtime->RequestFrontEndBypassOnce()",
            "UGameplayStatics::GetCurrentLevelName",
            "UGameplayStatics::OpenLevel",
        ):
            self.assertIn(token, controller)

        for token in (
            "RequestFrontEndBypassOnce",
            "ConsumeFrontEndBypassOnce",
            "bFrontEndBypassOnce",
        ):
            self.assertIn(token, runtime_h)
            self.assertIn(token, runtime_cpp)

    def test_front_end_uses_shared_settings_and_controls_pages(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("PauseMenuPage = ENarisPauseMenuPage::Settings", source)
        self.assertIn("PauseMenuPage = ENarisPauseMenuPage::Controls", source)

    def test_quit_uses_engine_quit_api(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("UKismetSystemLibrary::QuitGame", source)
        self.assertIn("EQuitPreference::Quit", source)

    def test_front_end_hides_gameplay_hud(self) -> None:
        hud = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("Controller->IsFrontEndMenuOpen()", hud)
        self.assertIn("DrawPauseMenu();", hud)
        front_index = hud.index("Controller->IsFrontEndMenuOpen()")
        hero_index = hud.index(
            "ANarisHeroCharacter* Hero = Cast<ANarisHeroCharacter>"
        )
        self.assertLess(front_index, hero_index)

    def test_front_end_strings_are_localized_in_en_and_ar(self) -> None:
        en = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/en/NARIS_Game.po"
        )
        ar = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/ar/NARIS_Game.po"
        )
        for key in (
            "FrontEndNewGame",
            "FrontEndContinue",
            "FrontEndQuit",
            "FrontEndNoSave",
            "FrontEndMenuHint",
        ):
            marker = f'msgctxt "NARIS,{key}"'
            self.assertIn(marker, en)
            self.assertIn(marker, ar)


if __name__ == "__main__":
    unittest.main()
