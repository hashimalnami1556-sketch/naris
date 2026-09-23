from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    return (ROOT/rel).read_text(encoding="utf-8")

class W04EnvironmentFactoryContractTests(unittest.TestCase):
    def test_factory_asset_is_registered(self):
        registry=json.loads(read("data/MASTER_ASSET_REGISTRY.json"))
        by_id={x.get("id"):x for x in registry.get("assets",[]) if isinstance(x,dict)}
        item=by_id["NARIS-W04-ENV-FACTORY-0002"]
        self.assertEqual(item["world"],"W04")
        self.assertEqual(item["domain"],"ENV")
        self.assertEqual(item["type"],"FACTORY")

    def test_blender_factory_reads_canonical_v2_config(self):
        source=read("tools/blender/NARIS_W04_ASHEN_FOREST_FACTORY_v2.py")
        for token in (
            "W04_AshenForest_environment_factory_v2.json",
            'SNAP_GRID = float(CONFIG["grid_m"])',
            'FLOOR_MODULE = float(CONFIG["modular_units"]["floor"])',
            'HEIGHT = float(CONFIG["modular_units"]["height"])',
            'STREAMING_CELL_M = float(CONFIG["streaming"]["cell_size_m"])',
            'root["grid_m"] = SNAP_GRID',
            'root["floor_module_m"] = FLOOR_MODULE',
            'root["streaming_cell_m"] = STREAMING_CELL_M',
            'root["collision_policy"] = json.dumps(CONFIG["collision"]',
            'root["lod_policy"] = json.dumps(CONFIG["lod"]',
        ):
            self.assertIn(token,source)
        self.assertNotIn("GRID = 4.0",source)
        self.assertNotIn('root["grid_m"]=GRID',source)
        self.assertNotIn('"32/80/160m"',source)

    def test_v2_config_distinguishes_snap_grid_from_floor_module(self):
        cfg=json.loads(read("data/environments/W04_AshenForest_environment_factory_v2.json"))
        self.assertEqual(cfg["grid_m"],1.0)
        self.assertEqual(cfg["modular_units"]["floor"],4.0)
        self.assertEqual(cfg["streaming"]["cell_size_m"],128)
        self.assertEqual(cfg["performance"]["material_slots_max_per_mesh"],4)

if __name__=="__main__":
    unittest.main()
