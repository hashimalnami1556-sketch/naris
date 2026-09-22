import json
import tempfile
import unittest
from pathlib import Path

from world_generator import BIOME_CATALOG, WorldConfig, build_world, export_world


class WorldGeneratorTests(unittest.TestCase):
    def test_catalog_has_99_biomes(self):
        self.assertEqual(99, len(BIOME_CATALOG))
        self.assertEqual(99, len(set(BIOME_CATALOG)))

    def test_build_is_deterministic(self):
        cfg = WorldConfig(seed=42, size=32, chunk_size=8, settlement_count=5, river_count=3)
        a = build_world(cfg)
        b = build_world(cfg)
        self.assertEqual(a["heightmap"], b["heightmap"])
        self.assertEqual(a["settlements"], b["settlements"])
        self.assertEqual(a["rivers"], b["rivers"])

    def test_expected_shapes_and_chunks(self):
        cfg = WorldConfig(seed=7, size=32, chunk_size=8, settlement_count=4, river_count=2)
        world = build_world(cfg)
        self.assertEqual(32, len(world["heightmap"]))
        self.assertTrue(all(len(row) == 32 for row in world["heightmap"]))
        self.assertEqual(16, len(world["chunks"]))
        self.assertEqual(99, len(world["biome_catalog"]))

    def test_export(self):
        cfg = WorldConfig(seed=1, size=16, chunk_size=8, settlement_count=2, river_count=1)
        world = build_world(cfg)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "world.json"
            export_world(world, out)
            loaded = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual("NARIS_ASSETFORGE_WORLD_GENERATOR", loaded["generator"])


if __name__ == "__main__":
    unittest.main()
