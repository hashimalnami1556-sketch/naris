from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
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


class PresentationBindingPathPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(BINDINGS.read_text(encoding="utf-8"))
        cls.assets = cls.data.get("assets", [])

    def test_bindings_use_v2_schema_and_path_policy(self) -> None:
        self.assertEqual(
            self.data["schema"],
            "naris.w04.presentation-bindings.v2",
        )
        self.assertIn("path_policy", self.data)

    def test_every_binding_has_unique_expected_object_path(self) -> None:
        expected = [
            item.get("expected_unreal_object_path")
            for item in self.assets
        ]
        self.assertTrue(all(expected))
        self.assertEqual(len(expected), len(set(expected)))

    def test_expected_path_matches_binding_kind(self) -> None:
        for item in self.assets:
            path = item["expected_unreal_object_path"]
            asset_id = item["asset_id"]
            sanitized = asset_id.replace("-", "_")

            if item["kind"] == "audio":
                self.assertIn("/Presentation/Audio/", path)
                self.assertTrue(path.endswith(f"/{sanitized}.{sanitized}"))
            elif item["kind"] == "vfx":
                self.assertIn("/Presentation/VFX/", path)
                self.assertTrue(path.endswith(f"/{sanitized}.{sanitized}"))
            elif item["kind"] == "camera":
                self.assertIn("/Presentation/Camera/", path)
                bp = f"BP_{sanitized}"
                self.assertTrue(path.endswith(f"/{bp}.{bp}_C"))
            else:
                self.fail(f"Unsupported presentation binding kind: {item['kind']}")

    def test_null_runtime_binding_is_explicit_not_fabricated(self) -> None:
        for item in self.assets:
            if item.get("unreal_object_path") is None:
                self.assertTrue(item.get("expected_unreal_object_path"))


if __name__ == "__main__":
    unittest.main()
