from __future__ import annotations

from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    return (ROOT/rel).read_text(encoding="utf-8")

class W04EnvironmentFactoryLauncherContractTests(unittest.TestCase):
    def test_factory_can_save_canonical_blend_source(self):
        source=read("tools/blender/NARIS_W04_ASHEN_FOREST_FACTORY_v2.py")
        for token in (
            'parser.add_argument("--out-blend")',
            "bpy.ops.wm.save_as_mainfile",
            "ensure_uv(o)",
            "bpy.ops.uv.smart_project",
        ):
            self.assertIn(token,source)

    def test_windows_launcher_runs_factory_then_existing_bridge(self):
        source=read("tools/windows/Invoke-NarisW04EnvironmentFactory.ps1")
        for token in (
            '$AssetId = "NARIS-W04-ENV-FACTORY-0002"',
            "NARIS_W04_ASHEN_FOREST_FACTORY_v2.py",
            "Invoke-NarisBlenderUnrealSmoke.ps1",
            "assets\\source\\blender\\W04",
            "--factory-startup",
            "--out-blend",
            "blender_manifest.json",
            '$manifestData.status -ne "pass"',
        ):
            self.assertIn(token,source)

    def test_launcher_does_not_claim_success_without_manifest(self):
        source=read("tools/windows/Invoke-NarisW04EnvironmentFactory.ps1")
        self.assertIn("Expected Blender exchange manifest was not produced",source)
        self.assertIn("manifest Asset ID mismatch",source)

if __name__=="__main__":
    unittest.main()
