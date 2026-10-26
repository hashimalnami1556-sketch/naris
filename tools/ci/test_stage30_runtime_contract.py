from pathlib import Path
import json, unittest

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=json.loads((ROOT/"data/stage30_runtime_manifest.json").read_text(encoding="utf-8"))
DOC=(ROOT/"docs/production/STAGE30_RUNTIME_INTEGRATION.md").read_text(encoding="utf-8")

class Stage30RuntimeContract(unittest.TestCase):
    def test_engine_and_shipping_gate(self):
        self.assertEqual(MANIFEST["engine"], "Unreal Engine 5.7")
        self.assertTrue(MANIFEST["runtime"]["shipping_blocked_until_pass"])
        self.assertEqual(MANIFEST["runtime"]["acceptance"], "PENDING_ASUSROG_ONLINE")

    def test_animation_contract(self):
        req=MANIFEST["animation"]["required"]
        for name in ("AnimBP","Attack Montage","Dodge Montage","Foot IK","AnimNotifies"):
            self.assertIn(name, req)
        self.assertIn("Attack>Recovery", MANIFEST["animation"]["transitions"])
        self.assertIn("Dodge>Recovery", MANIFEST["animation"]["transitions"])

    def test_pbr_contract(self):
        self.assertTrue(MANIFEST["materials"]["uv_required"])
        for ch in ("BaseColor","Normal","Roughness","AO"):
            self.assertIn(ch, MANIFEST["materials"]["required_channels"])

    def test_no_false_engine_pass(self):
        self.assertIn("ENGINE VALIDATION PENDING", DOC)
        self.assertIn("cannot mark Runtime or Visual QA as passed", DOC)

if __name__=="__main__":
    unittest.main()
