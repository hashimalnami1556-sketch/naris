"""WORLD-015: inspect actual GLB vertex/index bytes, not JSON-only impostors."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assetforge"))
from world015_gltf_gate import inspect_terrain_glb, check_tile_against_source


def example_glb(indices=(0, 1, 2, 1, 3, 2), empty_binary=False, bad_bounds=False):
    verts = [(-125., 0., 125.), (125., 0., 125.),
             (-125., 0., -125.), (125., 0., -125.)]
    indices_bin = struct.pack("<6H", *indices)
    verts_bin = b"".join(struct.pack("<fff", *v) for v in verts)
    blob = indices_bin + verts_bin
    manifest = {
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(indices_bin)},
            {"buffer": 0, "byteOffset": len(indices_bin), "byteLength": len(verts_bin)}],
        "accessors": [
            {"bufferView": 0, "componentType": 5123, "count": 6, "type": "SCALAR"},
            {"bufferView": 1, "componentType": 5126, "count": 4, "type": "VEC3",
             "min": [-125., 0., -125.],
             "max": [125., 200. if bad_bounds else 0., 125.]}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 1}, "indices": 0}]}],
    }
    json_bytes = json.dumps(manifest, separators=(",", ":")).encode()
    json_bytes += b" " * (-len(json_bytes) % 4)
    json_chunk = struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes
    bin_chunk = b"" if empty_binary else struct.pack("<I4s", len(blob), b"BIN\x00") + blob
    return struct.pack("<4sII", b"glTF", 2, 12 + len(json_chunk) + len(bin_chunk)) + json_chunk + bin_chunk


class World015BinaryIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "NR_Terrain_Example.glb"

    def test_valid_real_triangle_geometry_passes(self):
        self.path.write_bytes(example_glb())
        result = inspect_terrain_glb(self.path)
        self.assertEqual(result["triangles"], 2)
        self.assertEqual(result["height_min_m"], 0)
        self.assertEqual(result["width_m"], 250)
        self.assertTrue(check_tile_against_source(self.path, {
            "triangle_count": 2, "height_min_m": 0, "height_max_m": 0}))

    def test_json_only_glb_without_vertices_fails(self):
        self.path.write_bytes(example_glb(empty_binary=True))
        with self.assertRaisesRegex(ValueError, "BIN"):
            inspect_terrain_glb(self.path)

    def test_downward_winding_fails(self):
        self.path.write_bytes(example_glb(indices=(0, 2, 1, 1, 2, 3)))
        with self.assertRaisesRegex(ValueError, "Downward"):
            inspect_terrain_glb(self.path)

    def test_wrong_height_metadata_fails(self):
        self.path.write_bytes(example_glb())
        with self.assertRaisesRegex(ValueError, "elevation"):
            check_tile_against_source(self.path, {
                "triangle_count": 2, "height_min_m": -250, "height_max_m": 0})

    def test_out_of_range_triangle_index_fails(self):
        self.path.write_bytes(example_glb(indices=(0, 9, 2, 1, 3, 2)))
        with self.assertRaisesRegex(ValueError, "missing vertex"):
            inspect_terrain_glb(self.path)

    def test_fake_bounds_in_json_fail(self):
        self.path.write_bytes(example_glb(bad_bounds=True))
        with self.assertRaisesRegex(ValueError, "bounds"):
            inspect_terrain_glb(self.path)


if __name__ == "__main__":
    unittest.main()
