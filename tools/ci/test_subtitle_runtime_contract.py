from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class SubtitleRuntimeContractTests(unittest.TestCase):
    def test_subtitle_subsystem_is_data_driven_and_time_bounded(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisSubtitleSubsystem.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSubtitleSubsystem.cpp"
        )
        for token in (
            "UGameInstanceSubsystem",
            "ShowSubtitle",
            "ClearSubtitle",
            "IsSubtitleActive",
            "GetSpeaker",
            "GetLine",
            "GetRemainingSeconds",
            "OnSubtitleShown",
            "OnSubtitleCleared",
        ):
            self.assertIn(token, header)

        self.assertIn("Line.IsEmpty()", source)
        self.assertIn("DurationSeconds <= 0.f", source)
        self.assertIn("ExpiresAtGameTime", source)
        self.assertIn("World->GetTimeSeconds()", source)

    def test_hud_honors_subtitle_toggle_and_scale(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("void ANarisHUD::DrawSubtitle()", source)
        self.assertIn("!Settings->bSubtitlesEnabled", source)
        self.assertIn("Settings->SubtitleScale", source)
        self.assertIn("Subtitles->IsSubtitleActive()", source)
        self.assertIn("Subtitles->GetSpeaker()", source)
        self.assertIn("Subtitles->GetLine()", source)
        self.assertLess(
            source.rfind("DrawSubtitle();"),
            source.rfind("DrawPauseMenu();"),
        )

    def test_memory_crystal_accepts_authored_first_whisper_subtitle(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisMemoryCrystal.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisMemoryCrystal.cpp"
        )
        for token in (
            "FText SubtitleSpeaker",
            "FText SubtitleLine",
            "float SubtitleDurationSeconds = 4.f",
        ):
            self.assertIn(token, header)
        self.assertIn("if (!SubtitleLine.IsEmpty())", source)
        self.assertIn(
            "GameInstance->GetSubsystem<UNarisSubtitleSubsystem>()",
            source,
        )
        self.assertIn("Subtitles->ShowSubtitle(", source)

    def test_memory_crystal_does_not_fabricate_default_dialogue_line(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisMemoryCrystal.h"
        )
        self.assertIn("FText SubtitleSpeaker;", header)
        self.assertIn("FText SubtitleLine;", header)
        self.assertNotIn("SubtitleLine =", header)


if __name__ == "__main__":
    unittest.main()
