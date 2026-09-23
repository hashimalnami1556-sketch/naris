from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class GameUserSettingsAccessibilityContractTests(unittest.TestCase):
    def test_engine_registers_custom_game_user_settings_class(self) -> None:
        engine = read("unreal/NARIS_W04/Config/DefaultEngine.ini")
        self.assertIn(
            "GameUserSettingsClassName=/Script/NARIS_W04.NarisGameUserSettings",
            engine,
        )

    def test_settings_persist_graphics_audio_and_accessibility_fields(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameUserSettings.h"
        )
        for token in (
            "Config=GameUserSettings",
            "MasterVolume",
            "MusicVolume",
            "SFXVolume",
            "VoiceVolume",
            "bSubtitlesEnabled",
            "SubtitleScale",
            "bReduceCameraShake",
            "CameraShakeIntensity",
            "bHighContrastInteractions",
            "ColorVisionMode",
            "ColorVisionSeverity",
            "SetQualityPreset",
            "SetSubtitlesEnabled",
            "SetReduceCameraShake",
            "SetHighContrastInteractions",
            "SetCameraShakeIntensity",
            "SetColorVisionMode",
        ):
            self.assertIn(token, header)

    def test_defaults_and_validation_are_bounded(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisGameUserSettings.cpp"
        )
        for token in (
            "SetVSyncEnabled(true)",
            "SetFrameRateLimit(120.f)",
            "SetOverallScalabilityLevel(3)",
            "FMath::Clamp(MasterVolume, 0.f, 1.f)",
            "FMath::Clamp(SubtitleScale, 0.75f, 2.f)",
            "FMath::Clamp(CameraShakeIntensity, 0.f, 1.5f)",
            "FMath::Clamp(ColorVisionSeverity, 0.f, 1.f)",
            "ApplySettings(bCheckForCommandLineOverrides)",
        ):
            self.assertIn(token, source)

    def test_color_vision_correction_uses_unreal_accessibility_api(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisGameUserSettings.cpp"
        )
        self.assertIn(
            "UWidgetBlueprintLibrary::SetColorVisionDeficiencyType",
            source,
        )
        for token in ("Deuteranope", "Protanope", "Tritanope"):
            self.assertIn(token, source)

    def test_presentation_audio_uses_master_times_sfx_volume(self) -> None:
        settings = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisGameUserSettings.cpp"
        )
        presentation = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPresentationComponent.cpp"
        )
        self.assertIn("MasterVolume * SFXVolume", settings)
        self.assertIn("GetPresentationSFXScale()", presentation)
        self.assertIn("GetPresentationMusicScale()", presentation)
        self.assertIn("GetPresentationVoiceScale()", presentation)
        self.assertIn("Cue->VolumeMultiplier * AudioBusScale", presentation)

    def test_camera_shake_respects_reduction_and_user_intensity(self) -> None:
        settings = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisGameUserSettings.cpp"
        )
        presentation = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPresentationComponent.cpp"
        )
        self.assertIn("bReduceCameraShake", settings)
        self.assertIn("FMath::Min(AuthoredScale, 0.35f)", settings)
        self.assertIn("GetEffectiveCameraShakeScale()", presentation)
        self.assertIn("CameraManager->StartCameraShake", presentation)
        self.assertIn("SpatialScale", presentation)
        self.assertIn("EffectiveScale", presentation)

    def test_high_contrast_interaction_setting_changes_hud_prompt(self) -> None:
        hud = read("unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp")
        self.assertIn("bHighContrastInteractions", hud)
        self.assertIn("bHighContrast ? FLinearColor::White : Gold", hud)
        self.assertIn("bHighContrast ? 1.2f : 1.05f", hud)


if __name__ == "__main__":
    unittest.main()
