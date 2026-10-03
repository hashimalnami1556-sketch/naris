import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "tools" / "blender" / "NARIS_Blender_Master_Builder_v1_1.py"
REGISTRY = ROOT / "data" / "MASTER_ASSET_REGISTRY.json"
BINDINGS = ROOT / "unreal" / "NARIS_W04" / "Content" / "NARIS" / "W04" / "Production" / "W04_ProductionAssetBindings.json"
ENV = ROOT / "data" / "environments" / "W04_AshenForest_environment_factory_v2.json"

CORE_IDS = {
    "NARIS-W04-CHR-HERO-0001",
    "NARIS-W04-CHR-COMPANION-0001",
    "NARIS-W04-ENM-BONEBEAST-0001",
    "NARIS-W04-PRP-WAYSTONE-0001",
    "NARIS-W04-PRP-MEMORYCRYSTAL-0001",
    "NARIS-W04-PRP-ASHGATE-0001",
    "NARIS-W04-WPN-SWORD-0001",
}

class BlenderMasterBuilderV11ContractTests(unittest.TestCase):
    def test_builder_exists_and_python_syntax_compiles(self):
        source = BUILDER.read_text(encoding="utf-8")
        ast.parse(source)

    def test_builder_embeds_canonical_w04_core_ids(self):
        source = BUILDER.read_text(encoding="utf-8")
        for asset_id in CORE_IDS:
            self.assertIn(asset_id, source)

    def test_builder_targets_unreal_and_registry_gated_export(self):
        source = BUILDER.read_text(encoding="utf-8")
        for token in (
            "Unreal Engine 5.4",
            "MASTER_ASSET_REGISTRY.json",
            "W04_ProductionAssetBindings.json",
            "naris_export.py",
            "naris_asset_id",
            "expected_unreal_object_path",
        ):
            self.assertIn(token, source)

    def test_builder_uses_environment_factory_contract_not_conflicting_dimensions(self):
        source = BUILDER.read_text(encoding="utf-8")
        self.assertIn("W04_AshenForest_environment_factory_v2.json", source)
        self.assertIn("grid_m", source)
        self.assertIn("material_slots_max_per_mesh", source)
        self.assertIn("streaming", source)

    def test_builder_authors_all_seven_core_asset_roles(self):
        source = BUILDER.read_text(encoding="utf-8")
        for token in (
            '"waystone"',
            '"memory_crystal"',
            '"ash_gate"',
            "create_memory_crystal",
            'create_root("PRP_Waystone_ROOT"',
            "stamp_w04_asset(waystone",
            "stamp_w04_asset(memory_crystal",
            "stamp_w04_asset(ash_gate",
        ):
            self.assertIn(token, source)

    def test_memory_crystal_uses_supported_builder_primitive(self):
        source = BUILDER.read_text(encoding="utf-8")
        self.assertNotIn('add_primitive("ico","PRP_MemoryCrystal_Mesh"', source)

    def test_background_build_exits_nonzero_on_failure(self):
        source = BUILDER.read_text(encoding="utf-8")
        self.assertIn("sys.exit(1)", source)

    def test_builder_applies_export_transforms_and_keeps_weapon_asset_separate(self):
        source = BUILDER.read_text(encoding="utf-8")
        self.assertIn("bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)", source)
        self.assertNotIn("sword.parent=hero", source)

    def test_builder_has_strict_static_mesh_budget_validation(self):
        source = BUILDER.read_text(encoding="utf-8")
        for token in (
            "max_triangles_lod0",
            "max_material_slots",
            "naris_validation_errors",
            "triangle_count",
            "material_slot_count",
        ):
            self.assertIn(token, source)

    def test_core_ids_are_registered_and_bound(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
        registry_ids = {x.get("id") for x in registry.get("assets", [])}
        bound_ids = {x.get("asset_id") for x in bindings.get("assets", [])}
        self.assertTrue(CORE_IDS <= registry_ids)
        self.assertTrue(CORE_IDS <= bound_ids)

    def test_environment_contract_matches_w04_runtime_dimensions(self):
        env = json.loads(ENV.read_text(encoding="utf-8"))
        self.assertEqual(env["grid_m"], 1)
        self.assertEqual(env["modular_units"]["floor"], 4)
        self.assertEqual(env["modular_units"]["height"], 3.5)
        self.assertEqual(env["streaming"]["cell_size_m"], 128)
        self.assertEqual(env["performance"]["material_slots_max_per_mesh"], 4)

if __name__ == "__main__":
    unittest.main()
