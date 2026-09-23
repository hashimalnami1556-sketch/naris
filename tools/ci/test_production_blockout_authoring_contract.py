from __future__ import annotations

from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    return (ROOT/rel).read_text(encoding="utf-8")

class ProductionBlockoutAuthoringContractTests(unittest.TestCase):
    def test_authoring_uses_canonical_level_layout(self):
        source=read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_author_w04_production_blockout.py"
        )
        for token in (
            'MAP_PATH="/Game/NARIS/W04/Maps/W04_AshenForest_Blockout"',
            'LAYOUT_RELATIVE=Path("NARIS_MASTER")/"09_WORLD"/"Ashen_Forest"/"LEVEL_LAYOUT.json"',
            'f"BLOCKOUT_ZONE_{zone_id}"',
            'f"BLOCKOUT_MARKER_{zone_id}"',
            '"production_ready":False',
            '"shipping_allowed":False',
        ):
            self.assertIn(token,source)

    def test_blockout_places_core_progression_by_canonical_zone(self):
        source=read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_author_w04_production_blockout.py"
        )
        pairs=(
            ('"PlayerStart",unreal.PlayerStart,"Z01_FOREST_ENTRANCE"',),
            ('"NARIS_Waystone_0001",require_unreal_class("NarisWaystone"),"Z01_FOREST_ENTRANCE"',),
            ('"NARIS_MemoryCrystal_0001",require_unreal_class("NarisMemoryCrystal"),"Z02_BROKEN_SHRINE"',),
            ('"NARIS_CelestialWolf_0001",require_unreal_class("CelestialWolf"),"Z04_WHISPER_LAKE"',),
            ('"NARIS_AshGate_0001",require_unreal_class("NarisAshGate"),"Z05_ASH_GATE"',),
            ('"NARIS_BoneBeastBoss_0001",require_unreal_class("BoneBeastBoss"),"Z06_BONE_BEAST_ARENA"',),
        )
        for (token,) in pairs:
            self.assertIn(token,source)

    def test_windows_launcher_builds_editor_and_never_calls_blockout_shipping(self):
        source=read("tools/windows/Invoke-NarisW04ProductionBlockout.ps1")
        self.assertIn('"NARIS_W04Editor" "Win64" "Development"',source)
        self.assertIn("naris_author_w04_production_blockout.py",source)
        self.assertIn("W04_AshenForest_Blockout.umap",source)
        self.assertIn("This is NOT the Shipping map",source)
        self.assertNotIn("BuildCookRun",source)

if __name__=="__main__":
    unittest.main()
