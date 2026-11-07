"""WORLD-013 offline checker tests: complete package and intentionally damaged inputs."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from verify_world013_package import verify

ASSETS = [
    "Character 1.glb", "Character 3.glb",
    "Character1_NARIS_Rigged_Prototype.glb",
    "Environmental 1.glb", "City 1.glb",
]
UI = ["UI_MainMenu_Approved.png", "UI_Character_Approved.png", "UI_Combat_Approved.png"]


class World013PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.entries = {}
        for folder, names in (
            ("Source", ASSETS),
            ("Approved_UI", UI),
            ("Terrain/Chunks", [f"NR_Terrain_R{i:02}_C{j:02}.glb" for i in range(8) for j in range(8)]),
        ):
            destination = self.root / folder
            destination.mkdir(parents=True)
            group = []
            for name in names:
                sample = (folder + "/" + name).encode("utf-8")
                (destination / name).write_bytes(sample)
                item = {"filename": name, "sha256": hashlib.sha256(sample).hexdigest()}
                if folder == "Terrain/Chunks":
                    item["triangle_count"] = 7938
                group.append(item)
            self.entries[folder] = group
        raw = self.root / "Heightmaps/NARIS_2km_1009.r16"
        raw.parent.mkdir(parents=True)
        raw.write_bytes(b"\x00" * (1009 * 1009 * 2))
        self.manifest = {
            "schema": "naris.world013.1",
            "source_assets": self.entries["Source"],
            "original_ui_images": self.entries["Approved_UI"],
            "terrain_tiles": self.entries["Terrain/Chunks"],
            "scatter_count": 2990,
            "source_heightmap_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
            "default_map_modified": False,
        }
        self.persist()

    def persist(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest))

    def test_complete_package_is_offline_valid_only(self):
        result = verify(self.root)
        self.assertEqual(result["status"], "OFFLINE_FILES_VALID")
        self.assertFalse(result["unreal_run"])
        self.assertFalse(result["release_approved"])

    def test_modified_approved_image_blocks(self):
        (self.root / "Approved_UI/UI_Combat_Approved.png").write_bytes(b"changed")
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_missing_original_3d_model_blocks(self):
        (self.root / "Source/City 1.glb").unlink()
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_missing_terrain_tile_blocks(self):
        (self.root / "Terrain/Chunks/NR_Terrain_R07_C07.glb").unlink()
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_world_default_modification_blocks(self):
        self.manifest["default_map_modified"] = True
        self.persist()
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_missing_heightmap_blocks(self):
        (self.root / "Heightmaps/NARIS_2km_1009.r16").unlink()
        self.assertEqual(verify(self.root)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
