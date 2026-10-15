"""Separate production safety regression tests for Fiery Demon importer.

The production level must place the boss relative to the existing Ash Gate
marker, never an arbitrary hardcoded QA coordinate.
"""
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "unreal" / "import_fiery_demon_runtime.py"
LEVEL_REQUIREMENTS = Path(__file__).resolve().parents[2] / "unreal/NARIS_W04/Content/NARIS/W04/Maps/W04_ProductionMapRequirements.json"

class PlacementContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        ast.parse(cls.text)
    def test_production_anchor_is_canonical_ash_gate_actor(self):
        self.assertIn("NARIS_AshGate_0001",self.text)
        self.assertIn("NARIS_TARGET_MAP",self.text)
        self.assertIn("NARIS_ALLOW_MAP_EDIT",self.text)
    def test_missing_anchor_fails_without_saving_production(self):
        self.assertIn("Missing production Ash Gate anchor",self.text)
        self.assertIn("fail(",self.text)
    def test_prod_boss_spawn_uses_anchor_not_qa_coordinates(self):
        self.assertIn("get_actor_location()",self.text)
        self.assertIn("anchor",self.text)
        self.assertIn("spawn_boss_position",self.text)
    def test_fbx_reimports_are_idempotent_to_dedicated_directory(self):
        self.assertIn("task.replace_existing=True",self.text)
        self.assertIn('DEST = "/Game/NARIS/Enemies/FieryDemon"',self.text)
    def test_environment_is_optional_for_qa_only(self):
        self.assertIn("if target==QA_MAP",self.text)
        self.assertIn("place_environment(",self.text)
if __name__=="__main__":unittest.main()
