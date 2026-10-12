import json
import pathlib
import unittest
from validate_w04_encounters import validate

DATA = pathlib.Path(__file__).resolve().parents[2] / "data/gameplay/NARIS_W04_ENCOUNTERS_V1.json"

class EncounterTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(DATA.read_text(encoding="utf-8"))
    def test_all_three_zones_valid(self):
        self.assertEqual(validate(self.data), [])
    def test_reject_duplicate_zone(self):
        self.data["zones"][1]["id"] = self.data["zones"][0]["id"]
        self.assertIn("duplicate zone ids", validate(self.data))
    def test_reject_missing_boss(self):
        self.data["zones"][0]["boss"]["hp"] = 0
        self.assertTrue(any("invalid boss stats" in x for x in validate(self.data)))
    def test_reject_empty_attacks(self):
        self.data["zones"][0]["boss"]["phases"][0]["attack_set"] = []
        self.assertTrue(any("invalid boss phase" in x for x in validate(self.data)))
    def test_reject_fake_runtime_approval(self):
        self.data["integration"]["ue_editor_executed"] = True
        self.assertTrue(any("unverified engine" in x for x in validate(self.data)))

if __name__ == "__main__":
    unittest.main()
