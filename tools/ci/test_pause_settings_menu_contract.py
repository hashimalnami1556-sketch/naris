from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PauseSettingsMenuContractTests(unittest.TestCase):
    def test_game_mode_uses_naris_player_controller(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisGameMode.cpp"
        )
        self.assertIn('#include "NarisPlayerController.h"', source)
        self.assertIn(
            "PlayerControllerClass = ANarisPlayerController::StaticClass()",
            source,
        )

    def test_hero_pause_input_delegates_to_pause_menu(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        self.assertIn("Cast<ANarisPlayerController>(Controller)", source)
        self.assertIn("PlayerController->TogglePauseMenu()", source)
        self.assertIn("PauseBinding.bExecuteWhenPaused = true", source)

    def test_controller_owns_main_and_settings_pages(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisPlayerController.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        for token in (
            "ENarisPauseMenuPage",
            "TogglePauseMenu",
            "OpenPauseMenu",
            "ClosePauseMenu",
            "MenuUp",
            "MenuDown",
            "MenuLeft",
            "MenuRight",
            "MenuConfirm",
            "MenuBack",
            "GetMenuItemLabel",
            "GetMenuItemValue",
        ):
            self.assertIn(token, header)

        self.assertIn("constexpr int32 MainMenuCount = 2", source)
        self.assertIn("constexpr int32 SettingsMenuCount = 17", source)
        self.assertIn("UGameplayStatics::SetGamePaused(this, true)", source)
        self.assertIn("UGameplayStatics::SetGamePaused(this, false)", source)
        self.assertIn("Settings->ApplyAndSave(true)", source)
        self.assertIn("Settings->SetToDefaults()", source)

    def test_all_menu_navigation_executes_while_paused(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        for action in (
            "MenuUp",
            "MenuDown",
            "MenuLeft",
            "MenuRight",
            "MenuConfirm",
            "MenuBack",
        ):
            self.assertIn(f'BindPausedAction(TEXT("{action}")', source)
        self.assertIn("Binding.bExecuteWhenPaused = true", source)

    def test_keyboard_and_gamepad_menu_mappings_exist(self) -> None:
        ini = read("unreal/NARIS_W04/Config/DefaultInput.ini")
        for token in (
            'ActionName="MenuUp",Key=(KeyName="W")',
            'ActionName="MenuUp",Key=(KeyName="Gamepad_DPad_Up")',
            'ActionName="MenuDown",Key=(KeyName="S")',
            'ActionName="MenuDown",Key=(KeyName="Gamepad_DPad_Down")',
            'ActionName="MenuLeft",Key=(KeyName="A")',
            'ActionName="MenuRight",Key=(KeyName="D")',
            'ActionName="MenuConfirm",Key=(KeyName="Enter")',
            'ActionName="MenuConfirm",Key=(KeyName="Gamepad_FaceButton_Bottom")',
            'ActionName="MenuBack",Key=(KeyName="Escape")',
            'ActionName="MenuBack",Key=(KeyName="Gamepad_FaceButton_Right")',
        ):
            self.assertIn(token, ini)

    def test_settings_page_controls_graphics_audio_and_accessibility(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        for token in (
            "Settings->SetQualityPreset",
            "Settings->SetVSyncEnabled",
            "Settings->SetFrameRateLimit",
            "Settings->SetMasterVolume",
            "Settings->SetMusicVolume",
            "Settings->SetSFXVolume",
            "Settings->SetVoiceVolume",
            "Settings->SetCameraShakeIntensity",
            "Settings->SetReduceCameraShake",
            "Settings->SetSubtitlesEnabled",
            "Settings->SetSubtitleScale",
            "Settings->SetHighContrastInteractions",
            "Settings->SetColorVisionMode",
        ):
            self.assertIn(token, source)

    def test_hud_renders_pause_settings_overlay_last(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHUD.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("void DrawPauseMenu()", header)
        self.assertIn("void ANarisHUD::DrawPauseMenu()", source)
        self.assertIn("Controller->GetMenuItemLabel(Index)", source)
        self.assertIn("Controller->GetMenuItemValue(Index)", source)
        self.assertTrue(
            source.rfind("DrawPauseMenu();")
            > source.rfind("for (TActorIterator<ABoneBeastBoss>")
        )

    def test_pause_settings_strings_are_localized_in_en_and_ar(self) -> None:
        en = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/en/NARIS_Game.po"
        )
        ar = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/ar/NARIS_Game.po"
        )
        for key in (
            "PauseResume",
            "SettingsMenuTitle",
            "SettingsQuality",
            "SettingsMasterVolume",
            "SettingsSFXVolume",
            "SettingsCameraShake",
            "SettingsReduceCameraShake",
            "SettingsSubtitles",
            "SettingsHighContrast",
            "SettingsColorVision",
            "SettingsApplySave",
            "SettingsResetDefaults",
            "SettingsMenuHint",
        ):
            marker = f'msgctxt "NARIS,{key}"'
            self.assertIn(marker, en)
            self.assertIn(marker, ar)


if __name__ == "__main__":
    unittest.main()
