from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class FirstWhisperSubtitleContractTests(unittest.TestCase):
    def test_memory_crystal_has_localized_first_whisper_defaults(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisMemoryCrystal.cpp"
        )
        self.assertIn('"FirstWhisperSpeaker"', source)
        self.assertIn('"The First Whisper"', source)
        self.assertIn('"FirstWhisperLine"', source)
        self.assertIn(
            '"The gate remembers what the ash tried to bury."',
            source,
        )

    def test_memory_crystal_routes_line_through_subtitle_subsystem(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisMemoryCrystal.cpp"
        )
        self.assertIn("GetSubsystem<UNarisSubtitleSubsystem>()", source)
        self.assertIn("Subtitles->ShowSubtitle(", source)

    def test_hud_respects_subtitle_toggle_and_scale(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        for token in (
            "void ANarisHUD::DrawSubtitle()",
            "bSubtitlesEnabled",
            "SubtitleScale",
            "Subtitles->IsSubtitleActive()",
            "Subtitles->GetSpeaker()",
            "Subtitles->GetLine()",
        ):
            self.assertIn(token, source)

    def test_runtime_smoke_requires_visible_first_whisper_subtitle(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisRuntimeSmokeDirector.cpp"
        )
        self.assertIn('"first_whisper_subtitle"', source)
        self.assertIn("Subtitles->IsSubtitleActive()", source)
        self.assertIn("!Subtitles->GetLine().IsEmpty()", source)

    def test_first_whisper_is_localized_in_en_and_ar(self) -> None:
        en = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/en/NARIS_Game.po"
        )
        ar = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/ar/NARIS_Game.po"
        )
        for key in ("FirstWhisperSpeaker", "FirstWhisperLine"):
            marker = f'msgctxt "NARIS,{key}"'
            self.assertIn(marker, en)
            self.assertIn(marker, ar)


if __name__ == "__main__":
    unittest.main()
