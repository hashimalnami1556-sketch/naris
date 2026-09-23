from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "MASTER_ASSET_REGISTRY.json"
MANIFEST = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Presentation"
    / "W04_PresentationCueManifest.json"
)
BINDINGS = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Presentation"
    / "W04_PresentationAssetBindings.json"
)


class PresentationCueManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
        cls.by_id = {
            item["id"]: item
            for item in cls.registry.get("assets", [])
            if isinstance(item, dict) and "id" in item
        }

    def test_manifest_uses_expected_schema_and_runtime_bus(self) -> None:
        self.assertEqual(
            self.manifest["schema"],
            "naris.w04.presentation-cues.v1",
        )
        self.assertEqual(
            self.manifest["runtime_bus"],
            "UNarisPresentationComponent",
        )
        self.assertEqual(self.manifest["world"], "W04")

    def test_every_referenced_presentation_asset_is_registered_once(self) -> None:
        refs: set[str] = set()
        for cue in self.manifest.get("cues", []):
            for key in ("vfx", "audio", "camera"):
                value = cue.get(key)
                if value:
                    refs.add(value)

        for cue in self.manifest.get("dynamic_cues", []):
            for key in ("vfx", "audio", "camera"):
                value = cue.get(key)
                if value:
                    refs.add(value)

        ids = [
            item.get("id")
            for item in self.registry.get("assets", [])
            if isinstance(item, dict)
        ]
        for asset_id in sorted(refs):
            self.assertIn(asset_id, self.by_id, asset_id)
            self.assertEqual(ids.count(asset_id), 1, asset_id)
            self.assertEqual(self.by_id[asset_id]["world"], "W04")

    def test_vfx_audio_and_camera_refs_use_matching_domains(self) -> None:
        for cue in self.manifest.get("cues", []):
            if cue.get("vfx"):
                self.assertEqual(
                    self.by_id[cue["vfx"]]["domain"],
                    "VFX",
                )
            if cue.get("audio"):
                self.assertEqual(
                    self.by_id[cue["audio"]]["domain"],
                    "AUD",
                )
            if cue.get("camera"):
                self.assertEqual(
                    self.by_id[cue["camera"]]["domain"],
                    "CINE",
                )

    def test_every_referenced_asset_has_explicit_binding_record(self) -> None:
        binding_ids = [
            item["asset_id"]
            for item in self.bindings.get("assets", [])
            if isinstance(item, dict) and item.get("asset_id")
        ]
        refs: set[str] = set()
        for cue in self.manifest.get("cues", []) + self.manifest.get("dynamic_cues", []):
            for key in ("vfx", "audio", "camera"):
                if cue.get(key):
                    refs.add(cue[key])

        for asset_id in sorted(refs):
            self.assertEqual(binding_ids.count(asset_id), 1, asset_id)

    def test_dynamic_boss_attack_cue_remains_data_driven(self) -> None:
        dynamic = self.manifest.get("dynamic_cues", [])
        self.assertEqual(len(dynamic), 1)
        self.assertEqual(dynamic[0]["pattern"], "Boss.Attack.<AttackId>")
        self.assertEqual(dynamic[0]["runtime_cue"], "Boss.Attack.*")
        self.assertIn(
            "data-driven AttackId",
            dynamic[0]["note"],
        )
        self.assertIn("ClawSweep", dynamic[0]["note"])
        self.assertIn("BoneCharge", dynamic[0]["note"])
        self.assertIn("AshRupture", dynamic[0]["note"])


if __name__ == "__main__":
    unittest.main()
