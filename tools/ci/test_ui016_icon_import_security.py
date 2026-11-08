"""Behavioral UI-016 icon intake security regressions (no Unreal required)."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPORTER = ROOT / "tools/ui/import_naris_ui016_icons.py"
spec = importlib.util.spec_from_file_location("ui016_import", IMPORTER)
ui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui)


class IconImportSafetyTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.root.mkdir(exist_ok=True)
        self.valid_manifest = {
            "original_ui_images": [
                {"filename": filename, "sha256": digest}
                for filename, digest in ui.PINNED_UI_SHA256.items()
            ],
            "ui_vector_icons": [
                {
                    "name": name, "png_filename": name + ".png",
                    "png_sha256": digest, "svg_filename": name + ".svg",
                    "svg_sha256": "0" * 64,
                }
                for name, digest in ui.PINNED_ICON_PNG_SHA256.items()
            ]
        }

    def write_manifest(self):
        (self.root / "manifest.json").write_text(
            json.dumps(self.valid_manifest), encoding="utf-8"
        )

    def test_locked_screenshot_hashes_match_repo_approval(self):
        manifest = json.loads(
            (ROOT / "docs/ui/references/UI-002/manifest.json").read_text(encoding="utf-8")
        )
        got = {entry["file"]: entry["sha256"] for entry in manifest["images"]}
        self.assertEqual(ui.PINNED_UI_SHA256, got)

    def test_six_icons_are_named_and_pinned(self):
        self.assertEqual(
            set(ui.PINNED_ICON_PNG_SHA256), {"health", "energy", "mana", "attack", "defense", "map"}
        )
        self.assertTrue(all(len(sha) == 64 for sha in ui.PINNED_ICON_PNG_SHA256.values()))

    def test_missing_original_source_files_block_import(self):
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "Missing/modified approved source"):
            ui.validate_inputs(self.root)

    def test_mutated_manifest_cannot_override_approved_image_hash(self):
        self.valid_manifest["original_ui_images"][0]["sha256"] = "0" * 64
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "locked source"):
            ui.validate_inputs(self.root)

    def test_an_invented_seventh_icon_is_rejected(self):
        self.valid_manifest["ui_vector_icons"][0]["name"] = "fictitious"
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "exact six"):
            ui.validate_inputs(self.root)

    def test_missing_approved_screenshot_blocked(self):
        self.valid_manifest["original_ui_images"].pop()
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "Three original approved screenshots"):
            ui.validate_inputs(self.root)

    def test_icon_svg_hash_cannot_be_redefined_by_manifest(self):
        self.write_manifest()
        approved = self.root / "Approved_UI"
        approved.mkdir()
        for name in ui.PINNED_UI_SHA256:
            (approved / name).write_bytes(b"original-source-proxy")
        self.valid_manifest["ui_vector_icons"][0]["svg_sha256"] = "f" * 64
        self.write_manifest()
        from unittest.mock import patch
        with patch.object(ui, "checksum", side_effect=lambda path: ui.PINNED_UI_SHA256.get(path.name, "")):
            with self.assertRaisesRegex(ValueError, "locked vector source"):
                ui.validate_inputs(self.root)

    def test_icon_png_hash_cannot_be_redefined_by_manifest(self):
        # Verify screenshot files to reach the icon metadata check.
        self.write_manifest()
        approved = self.root / "Approved_UI"
        approved.mkdir()
        for name in ui.PINNED_UI_SHA256:
            (approved / name).write_bytes(b"original-source-proxy")
        self.valid_manifest["ui_vector_icons"][0]["png_sha256"] = "0" * 64
        self.write_manifest()
        from unittest.mock import patch
        with patch.object(ui, "checksum", side_effect=lambda path: ui.PINNED_UI_SHA256.get(path.name, "")):
            with self.assertRaisesRegex(ValueError, "locked source"):
                ui.validate_inputs(self.root)


if __name__ == "__main__":
    unittest.main()
