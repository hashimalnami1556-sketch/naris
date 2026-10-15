"""Offline regression checks. These do not require Unreal or claim PIE verification."""
import ast
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).with_name("import_and_place_fiery_demon.py")

class ImportAndPlaceTests(unittest.TestCase):
    def setUp(self):
        self.source = SCRIPT.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)
    def test_guards_production_map_writes(self):
        self.assertIn("NARIS_ALLOW_MAP_EDIT", self.source)
        self.assertIn("Refusing to edit production map", self.source)
    def test_imports_skeletal_mesh_and_animations(self):
        self.assertIn("FBXIT_SKELETAL_MESH", self.source)
        self.assertIn("import_animations = True", self.source)
    def test_idempotent_actor_label(self):
        self.assertIn('a.get_actor_label() == "NARIS_FieryDemon_EliteBoss"', self.source)
    def test_no_false_combat_verification(self):
        self.assertIn('"boss_ai_active":False',self.source)
        self.assertIn('"pie_tested":False',self.source)
    def test_level_is_saved(self):
        self.assertIn("save_current_level()",self.source)

if __name__=="__main__": unittest.main()
