from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "MASTER_ASSET_REGISTRY.json"
SCHEMA = ROOT / "schemas" / "naris_blender_exchange.schema.json"
FIXTURES = ROOT / "tools" / "ci" / "fixtures"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class BlenderUnrealBridgeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_json(REGISTRY)
        cls.schema = load_json(SCHEMA)
        cls.assets = {
            item["id"]: item
            for item in cls.registry.get("assets", [])
            if isinstance(item, dict) and "id" in item
        }
        cls.pattern = re.compile(cls.schema["properties"]["asset_id"]["pattern"])

    def validate_manifest_shape(self, manifest: dict) -> None:
        required = set(self.schema["required"])
        self.assertTrue(required.issubset(manifest.keys()))
        self.assertRegex(manifest["asset_id"], self.pattern)
        self.assertIn(manifest["status"], {"pass", "fail"})
        self.assertIsInstance(manifest["objects"], list)
        self.assertIsInstance(manifest["issues"], list)

    def test_waystone_manifest_is_registered_and_consistent(self) -> None:
        manifest = load_json(FIXTURES / "waystone_valid_manifest.json")
        self.validate_manifest_shape(manifest)

        asset_id = manifest["asset_id"]
        self.assertEqual(manifest["status"], "pass")
        self.assertEqual(manifest["registry_status"], "registered")
        self.assertIn(asset_id, self.assets)
        self.assertEqual(self.assets[asset_id]["world"], "W04")
        self.assertEqual(manifest["registry_entry"]["id"], asset_id)
        self.assertEqual(manifest["registry_entry"]["world"], self.assets[asset_id]["world"])
        self.assertEqual(manifest["issues"], [])
        self.assertGreater(len(manifest["objects"]), 0)

    def test_unregistered_manifest_is_rejected_by_contract(self) -> None:
        manifest = load_json(FIXTURES / "unregistered_manifest.json")
        self.validate_manifest_shape(manifest)

        self.assertEqual(manifest["status"], "fail")
        self.assertEqual(manifest["registry_status"], "unregistered")
        self.assertNotIn(manifest["asset_id"], self.assets)
        self.assertIsNone(manifest["registry_entry"])
        self.assertGreater(len(manifest["issues"]), 0)

    def test_registry_has_unique_asset_ids(self) -> None:
        ids = [
            item["id"]
            for item in self.registry.get("assets", [])
            if isinstance(item, dict) and "id" in item
        ]
        self.assertEqual(len(ids), len(set(ids)))

    def test_unreal_importer_rechecks_master_registry(self) -> None:
        source = (
            ROOT
            / "unreal"
            / "NARIS_W04"
            / "Content"
            / "Python"
            / "naris_import_blender_exchange.py"
        ).read_text(encoding="utf-8")

        for token in (
            "NARIS_MASTER_REGISTRY",
            "load_registry_entry",
            "registry_status",
            "registry_entry",
            "NARIS.RegistryStatus",
        ):
            self.assertIn(token, source)

    def test_windows_smoke_script_gates_before_execution(self) -> None:
        source = (
            ROOT
            / "tools"
            / "windows"
            / "Invoke-NarisBlenderUnrealSmoke.ps1"
        ).read_text(encoding="utf-8")

        for token in (
            "MASTER_ASSET_REGISTRY.json",
            "ConvertFrom-Json",
            "registryMatches.Count -ne 1",
            "NARIS_MASTER_REGISTRY",
            "NARIS_EXCHANGE_MANIFEST",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
