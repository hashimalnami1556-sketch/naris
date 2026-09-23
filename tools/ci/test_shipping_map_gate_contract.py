from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    return (ROOT/rel).read_text(encoding="utf-8")

class ShippingMapGateContractTests(unittest.TestCase):
    def test_requirements_match_world_level_layout(self):
        layout=json.loads(read("NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json"))
        req=json.loads(read(
            "unreal/NARIS_W04/Content/NARIS/W04/Maps/"
            "W04_ProductionMapRequirements.json"
        ))
        self.assertEqual(req["production_map"],"/Game/NARIS/W04/Maps/W04_AshenForest")
        self.assertEqual(req["bounds_m"],layout["bounds_m"])
        self.assertEqual(
            [z["id"] for z in req["zones"]],
            [z["id"] for z in layout["zones"]],
        )
        self.assertEqual(req["critical_path"],layout["critical_path"])
        self.assertEqual(len(req["zones"]),6)
        self.assertEqual(
            set(req["required_actor_classes"]),
            {"DirectionalLight","SkyLight","ExponentialHeightFog","NavMeshBoundsVolume"},
        )
        self.assertEqual(
            set(req["forbidden_label_prefixes"]),
            {"DEV_","BLOCKOUT_"},
        )

    def test_validator_is_data_driven_and_rejects_smoke_content(self):
        source=read("unreal/NARIS_W04/Content/Python/naris_validate_shipping_map.py")
        for token in (
            "W04_ProductionMapRequirements.json",
            "required_actor_labels",
            'zone["label"]',
            "required_actor_classes",
            "forbidden_actor_labels",
            "forbidden_label_prefixes",
            "missing_actor_classes",
            "Development/smoke/blockout actors exist in production map",
            "naris_shipping_map_validation.json",
        ):
            self.assertIn(token,source)

    def test_release_candidate_runs_shipping_map_validator(self):
        source=read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        self.assertIn("naris_validate_shipping_map.py",source)
        self.assertIn("[NARIS RC] Validating production Ashen Forest map",source)
        self.assertIn("shipping_map_validation_status",source)

    def test_release_candidate_cooks_production_map_not_smoke_map(self):
        source=read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        self.assertIn('"-map=W04_AshenForest"',source)
        self.assertNotIn('"-map=W04_Prototype"',source)

if __name__=="__main__":
    unittest.main()
