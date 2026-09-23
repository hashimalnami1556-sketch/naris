from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PLAN = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Presentation"
    / "W04_PresentationSourcePlan.json"
)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PresentationAudioIntakeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(PLAN.read_text(encoding="utf-8"))
        cls.audio = [
            item for item in cls.plan.get("assets", [])
            if item.get("kind") == "audio"
        ]

    def test_source_plan_declares_all_sixteen_audio_sources(self) -> None:
        self.assertEqual(len(self.audio), 16)
        for item in self.audio:
            self.assertEqual(
                item["source_file"],
                f"assets/source/presentation/audio/{item['asset_id']}.wav",
            )
            contract = item["source_contract"]
            self.assertEqual(contract["preferred_source"], "WAV")
            self.assertEqual(contract["sample_rate_hz"], 48000)
            self.assertEqual(contract["bit_depth"], 24)
            self.assertEqual(contract["encoding"], "PCM")

    def test_audio_importer_validates_pcm_master_before_import(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_import_presentation_audio.py"
        )
        for token in (
            "wave.open",
            "sample_rate != 48000",
            "sample_width != 3",
            "channels not in (1, 2)",
            'compression != "NONE"',
            "duration > 30.0",
        ):
            self.assertIn(token, source)

    def test_audio_importer_is_non_fabricating(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_import_presentation_audio.py"
        )
        self.assertIn("if not source_path.is_file():", source)
        self.assertIn("skipped_missing.append(asset_id)", source)
        self.assertNotIn("create_asset(", source)
        self.assertNotIn("generate_sound_effect", source)
        self.assertNotIn('wave.open(str(source_path), "wb")', source)

    def test_audio_importer_uses_automated_asset_import_task(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_import_presentation_audio.py"
        )
        for token in (
            "unreal.AssetImportTask()",
            '"destination_path"',
            '"destination_name"',
            '"automated"',
            '"replace_existing"',
            '"save"',
            "asset_tools.import_asset_tasks",
            "isinstance(obj, unreal.SoundBase)",
        ):
            self.assertIn(token, source)

    def test_bootstrap_orders_audio_before_binding_resolution(self) -> None:
        source = read("tools/windows/Invoke-NarisW04AuthoringBootstrap.ps1")
        audio_index = source.index(
            "[NARIS] Importing validated presentation WAV sources"
        )
        resolver_index = source.index(
            "[NARIS] Resolving real presentation payloads at deterministic paths"
        )
        profile_index = source.index(
            "[NARIS] Building/loading shared W04 presentation profile"
        )
        self.assertLess(audio_index, resolver_index)
        self.assertLess(resolver_index, profile_index)

    def test_windows_package_archives_audio_evidence(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            "naris_presentation_audio_import.json",
            "presentation_audio_import_status",
            "presentation_audio_imported_asset_ids",
            "presentation_audio_missing_asset_ids",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
