"""Strict release preflight regression tests. Execute: python -m unittest discover -s tools/ci -p test_ui006_release_gate.py"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from verify_ui_world_release import check


class UIWorldReleaseGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "unreal/NARIS_W04"
        src = self.project / "Source/NARIS_W04/Private"
        src.mkdir(parents=True)
        (self.project / "NARIS_W04.uproject").write_text("{}")
        (src / "NarisSystemMenuWidget.cpp").write_text(
            "FAnchors(0.71f, 0.27f, 0.95f, 0.83f) State.EquippedItems[Index] State.InventoryItems[Index]")
        (src / "NarisHUD.cpp").write_text(
            "const float Y = Safe + 12.f * Scale; Boss->GetCurrentHealth() Boss->GetConfiguredMaxHealth()")
        (self.project / "Config").mkdir()
        (self.project / "Config/DefaultEngine.ini").write_text(
            "GameDefaultMap=/Game/NARIS/W04/Maps/W04_AshenForest")
        folder = self.project / "Content/NARIS/W04/Maps"
        folder.mkdir(parents=True)
        (folder / "W04_AshenForest.umap").write_bytes(b"x" * 2048)
        self.refs = self.root / "refs"
        self.refs.mkdir()
        entries = []
        for name in ("UI_MainMenu_Approved.png", "UI_Character_Approved.png", "UI_Combat_Approved.png"):
            payload = name.encode()
            (self.refs / name).write_bytes(payload)
            entries.append({"file": name, "sha256": hashlib.sha256(payload).hexdigest()})
        p = self.root / "docs/ui/references/UI-002"
        p.mkdir(parents=True)
        (p / "manifest.json").write_text(json.dumps({"images": entries}))

    def test_complete_offline_contract_passes_but_not_runtime(self):
        result = check(self.root, self.refs)
        self.assertEqual(result["status"], "PASS_OFFLINE_PREFLIGHT")
        self.assertFalse(result["unreal_runtime_verified"])

    def test_missing_production_map_blocks(self):
        (self.project / "Content/NARIS/W04/Maps/W04_AshenForest.umap").unlink()
        self.assertEqual(check(self.root, self.refs)["status"], "BLOCKED")

    def test_wrong_default_map_blocks(self):
        (self.project / "Config/DefaultEngine.ini").write_text(
            "GameDefaultMap=/Game/NARIS/W04/Maps/W04_Prototype")
        self.assertFalse(check(self.root, self.refs)["checks"]["production_map_default"])

    def test_changed_original_png_blocks(self):
        (self.refs / "UI_Combat_Approved.png").write_bytes(b"tampered")
        self.assertFalse(check(self.root, self.refs)["checks"]["approved_ui_png_sha256"])

    def test_missing_live_inventory_blocks(self):
        p = self.project / "Source/NARIS_W04/Private/NarisSystemMenuWidget.cpp"
        p.write_text("FAnchors(0.71f, 0.27f, 0.95f, 0.83f)")
        self.assertFalse(check(self.root, self.refs)["checks"]["live_inventory"])


if __name__ == "__main__":
    unittest.main()
