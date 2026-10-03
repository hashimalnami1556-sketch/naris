import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LAUNCHER=ROOT/"tools"/"windows"/"Invoke-NarisBlenderMasterBuilder.ps1"

class BlenderMasterBuilderLauncherContractTests(unittest.TestCase):
    def test_launcher_exists_and_contains_pipeline_contract(self):
        text=LAUNCHER.read_text(encoding="utf-8")
        for token in (
            "NARIS_Blender_Master_Builder_v1_1.py",
            "NARIS_REPO_ROOT",
            "blender.exe",
            "--background",
            "naris_export.py",
            "MASTER_ASSET_REGISTRY.json",
            "NARIS-W04-CHR-HERO-0001",
            "NARIS-W04-CHR-COMPANION-0001",
            "NARIS-W04-ENM-BONEBEAST-0001",
            "NARIS-W04-PRP-WAYSTONE-0001",
            "NARIS-W04-PRP-MEMORYCRYSTAL-0001",
            "NARIS-W04-PRP-ASHGATE-0001",
            "NARIS-W04-WPN-SWORD-0001",
        ):
            self.assertIn(token,text)

    def test_launcher_writes_json_evidence_without_utf8_bom(self):
        text=LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("UTF8Encoding($false)", text)
        self.assertNotIn("Set-Content -Encoding UTF8", text)

    def test_launcher_retains_local_evidence(self):
        text=LAUNCHER.read_text(encoding="utf-8")
        for token in ("artifacts", "validation", "manifest", "NARIS_Master_W04.blend", "if (-not (Test-Path $BlendFile))", "throw"):
            self.assertIn(token,text)

if __name__=="__main__":
    unittest.main()
