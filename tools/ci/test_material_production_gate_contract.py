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
    / "Materials"
    / "W04_MaterialBindings.json"
)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class MaterialProductionGateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
        cls.library = json.loads(
            read("data/materials/W04_ASHEN_FOREST_MATERIAL_LIBRARY_v1.json")
        )
        cls.registry = json.loads(read("data/MASTER_ASSET_REGISTRY.json"))

    def test_bindings_register_ten_canonical_material_assets(self) -> None:
        self.assertEqual(
            self.bindings["schema"],
            "naris.w04.material-bindings.v1",
        )
        assets = self.bindings["assets"]
        self.assertEqual(len(assets), 10)

        registry_ids = {
            item.get("id")
            for item in self.registry.get("assets", [])
            if isinstance(item, dict)
        }
        for item in assets:
            self.assertIn(item["asset_id"], registry_ids)
            self.assertTrue(item["asset_id"].startswith("NARIS-W04-MAT-"))
            self.assertEqual(
                item["expected_class"],
                "MaterialInstanceConstant",
            )
            self.assertTrue(
                item["expected_unreal_object_path"].startswith(
                    "/Game/NARIS/W04/Materials/MI_"
                )
            )

    def test_surface_and_water_parent_contracts_are_explicit(self) -> None:
        assets = self.bindings["assets"]
        surface = [item for item in assets if item["profile"] == "surface"]
        water = [item for item in assets if item["profile"] == "water"]
        self.assertEqual(len(surface), 9)
        self.assertEqual(len(water), 1)

        surface_master = (
            "/Game/NARIS/Materials/"
            "M_MASTER_SURFACE.M_MASTER_SURFACE"
        )
        water_master = (
            "/Game/NARIS/Materials/"
            "M_MASTER_WATER.M_MASTER_WATER"
        )
        for item in surface:
            self.assertEqual(item["expected_parent"], surface_master)
        self.assertEqual(water[0]["expected_parent"], water_master)

    def test_bindings_cover_every_library_material_id(self) -> None:
        expected = {
            item["id"]
            for item in self.library.get("materials", [])
        }
        expected.add(self.library["water"]["id"])
        actual = {
            item["material_library_id"]
            for item in self.bindings["assets"]
        }
        self.assertEqual(actual, expected)

    def test_material_validator_checks_parent_and_pbr_parameters(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_validate_material_bindings.py"
        )
        for token in (
            "unreal.MaterialInstanceConstant",
            'instance.get_editor_property("parent")',
            "get_material_instance_scalar_parameter_value",
            "get_material_instance_vector_parameter_value",
            "TOLERANCE = 0.02",
            "material parameters do not match library",
            "NARIS_MATERIALS_STRICT",
            "naris_material_validation.json",
        ):
            self.assertIn(token, source)

    def test_bootstrap_development_and_shipping_wire_material_gate(self) -> None:
        bootstrap = read("tools/windows/Invoke-NarisW04AuthoringBootstrap.ps1")
        package = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        rc = read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")

        self.assertIn("naris_validate_material_bindings.py", bootstrap)
        self.assertIn("naris_material_validation.json", package)
        self.assertIn("material_validation_status", package)

        for token in (
            'NARIS_MATERIALS_STRICT = "1"',
            "Strict material validation did not pass",
            "Release candidate has unresolved W04 material instances",
            "Release candidate has unresolved W04 master materials",
            "Release candidate material validation contains errors",
            "material_unresolved_count",
            "material_unresolved_master_count",
            "material_error_count",
        ):
            self.assertIn(token, rc)


if __name__ == "__main__":
    unittest.main()
