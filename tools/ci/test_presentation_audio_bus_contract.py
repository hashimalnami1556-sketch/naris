from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PresentationAudioBusContractTests(unittest.TestCase):
    def test_runtime_cue_struct_exposes_three_audio_buses(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/"
            "NarisPresentationComponent.h"
        )
        for token in (
            "enum class ENarisPresentationAudioBus",
            "SFX",
            "MUSIC",
            "VOICE",
            "ENarisPresentationAudioBus AudioBus",
        ):
            self.assertIn(token, header)

    def test_user_settings_expose_master_times_each_bus_scale(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/"
            "NarisGameUserSettings.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisGameUserSettings.cpp"
        )
        for token in (
            "GetPresentationSFXScale",
            "GetPresentationMusicScale",
            "GetPresentationVoiceScale",
        ):
            self.assertIn(token, header)
            self.assertIn(token, source)

        self.assertIn("MasterVolume * SFXVolume", source)
        self.assertIn("MasterVolume * MusicVolume", source)
        self.assertIn("MasterVolume * VoiceVolume", source)

    def test_presentation_runtime_selects_volume_by_audio_bus(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisPresentationComponent.cpp"
        )
        for token in (
            "switch (Cue->AudioBus)",
            "ENarisPresentationAudioBus::MUSIC",
            "GetPresentationMusicScale()",
            "ENarisPresentationAudioBus::VOICE",
            "GetPresentationVoiceScale()",
            "ENarisPresentationAudioBus::SFX",
            "GetPresentationSFXScale()",
            "Cue->VolumeMultiplier * AudioBusScale",
        ):
            self.assertIn(token, source)

    def test_profile_authoring_maps_manifest_bus_to_reflected_enum(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_build_presentation_profile.py"
        )
        for token in (
            "def resolve_audio_bus(",
            '"sfx": "SFX"',
            '"music": "MUSIC"',
            '"voice": "VOICE"',
            'cue.set_editor_property(',
            '"audio_bus"',
            "has audio but no audio_bus",
            "declares audio_bus without audio",
        ):
            self.assertIn(token, source)

    def test_dynamic_cues_preserve_audio_bus_during_authoring(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_build_presentation_profile.py"
        )
        self.assertIn(
            '("vfx", "audio", "camera", "audio_bus")',
            source,
        )


if __name__ == "__main__":
    unittest.main()
