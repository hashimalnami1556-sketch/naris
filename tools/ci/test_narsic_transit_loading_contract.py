"""Static CI contract for CALL OF NARIS approved transit loading screen.

No Unreal runtime build is claimed by these source-only checks.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ApprovedTransitLoadingContract(unittest.TestCase):
    def test_art_approval_manifest(self):
        d = json.loads(source("assets/NARSIC_TRANSIT_APPROVED_ASSET.json"))
        self.assertEqual(d["product"], "CALL OF NARIS")
        self.assertEqual(d["width"], 1672)
        self.assertEqual(d["height"], 941)
        self.assertEqual(len(d["sha256"]), 64)

    def test_movieplayer_is_bound_to_actual_map_load(self):
        cpp = source("unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.cpp")
        self.assertIn("MoviePlayer.h", cpp)
        self.assertIn("PreLoadMap.AddRaw", cpp)
        self.assertIn("PostLoadMapWithWorld.AddRaw", cpp)
        self.assertIn("bAutoCompleteWhenLoadingCompletes = true", cpp)
        self.assertIn("FSlateDynamicImageBrush", cpp)
        self.assertIn("NARSIC_Transit_Approved.png", cpp)
        self.assertIn("SThrobber", cpp)
        self.assertNotIn('TEXT("62%")', cpp)

    def test_packaging_and_dependencies(self):
        build = source("unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.Build.cs")
        config = source("unreal/NARIS_W04/Config/DefaultGame.ini")
        self.assertIn('"MoviePlayer"', build)
        self.assertIn('DirectoriesToAlwaysStageAsNonUFS=(Path="NARSIC/Loading")', config)

    def test_exact_public_name(self):
        cpp = source("unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.cpp")
        ini = source("unreal/NARIS_W04/Config/DefaultEngine.ini")
        self.assertIn('TEXT("CALL OF NARIS")', cpp)
        self.assertIn("ProjectName=CALL OF NARIS", ini)


if __name__ == "__main__":
    unittest.main()
