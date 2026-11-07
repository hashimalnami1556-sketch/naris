"""Offline WORLD-014 ground sampling contract: never fabricate Z=0 for landmarks."""
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assetforge"))
from world014_ground_alignment import (
    GRID, corrected_landmarks, landmark_ground_m
)


class World014GroundAlignment(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.map = Path(self.tmp.name) / "world.r16"
        raw = bytearray(b"\x00\x80" * (GRID * GRID))
        center = 504
        struct.pack_into("<H", raw, 2 * (center * GRID + center), 33408)
        self.map.write_bytes(raw)

    def test_zero_zero_sample_is_five_metres(self):
        self.assertEqual(landmark_ground_m(self.map, 0, 0), 5.0)

    def test_outside_world_extent_is_blocked(self):
        with self.assertRaises(ValueError):
            landmark_ground_m(self.map, 1001, 0)

    def test_truncated_map_is_blocked(self):
        self.map.write_bytes(b"\x00")
        with self.assertRaises(ValueError):
            landmark_ground_m(self.map, 0, 0)

    def test_manifest_correction_does_not_mutate_input(self):
        original = {"environment_landmarks": [{"location_m_xyz": [0, 0, 0]}]}
        output = corrected_landmarks(original, self.map)
        self.assertEqual(output["environment_landmarks"][0]["location_m_xyz"][2], 5)
        self.assertEqual(original["environment_landmarks"][0]["location_m_xyz"][2], 0)

    def test_bad_source_hash_is_blocked(self):
        with self.assertRaises(ValueError):
            landmark_ground_m(self.map, 0, 0, "0" * 64)


if __name__ == "__main__":
    unittest.main()
