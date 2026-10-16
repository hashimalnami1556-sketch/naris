import json
import struct
import tempfile
import unittest
from pathlib import Path

from world_exporters import export_biome_masks_pgm, export_heightmap_r16, export_world_rasters


class WorldExporterTests(unittest.TestCase):
    def test_r16_size_and_endpoints(self):
        grid = [[0.0, 1.0], [0.5, 1.5]]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "h.r16"
            export_heightmap_r16(grid, path)
            data = path.read_bytes()
            self.assertEqual(8, len(data))
            self.assertEqual((0, 65535, 32768, 65535), struct.unpack(">4H", data))

    def test_biome_masks_are_deterministic_and_binary(self):
        grid = [["ashen", "forest"], ["ashen", "ashen"]]
        with tempfile.TemporaryDirectory() as tmp:
            paths = export_biome_masks_pgm(grid, Path(tmp))
            self.assertEqual(["biome_ashen.pgm", "biome_forest.pgm"], [p.name for p in paths])
            self.assertTrue(paths[0].read_bytes().endswith(bytes([255, 0, 255, 255])))

    def test_manifest(self):
        world = {
            "generator": "NARIS_ASSETFORGE_WORLD_GENERATOR",
            "heightmap": [[0.0, 1.0], [0.25, 0.75]],
            "biomes": [["a", "b"], ["a", "b"]],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = export_world_rasters(world, root)
            loaded = json.loads((root / "raster_manifest.json").read_text())
            self.assertEqual(manifest, loaded)
            self.assertEqual("R16_BE_UINT16", loaded["heightmap_format"])
            self.assertEqual(2, len(loaded["biome_masks"]))

    def test_rejects_non_square_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                export_heightmap_r16([[0.0, 1.0], [0.5]], Path(tmp) / "bad.r16")


if __name__ == "__main__":
    unittest.main()
