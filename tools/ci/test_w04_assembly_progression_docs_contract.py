from __future__ import annotations

from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    return (ROOT/rel).read_text(encoding="utf-8")

class W04AssemblyProgressionDocsContractTests(unittest.TestCase):
    def test_playable_assembly_matches_runtime_quest_order(self):
        assembly=read(
            "unreal/NARIS_W04/Content/NARIS/W04/Maps/"
            "W04_PlayableAssembly_Spec.md"
        )
        order=[
            "Broken Shrine / Memory Crystal",
            "Ash Gate",
            "Celestial Wolf",
            "Bone Beast Arena",
            "Demo End",
        ]
        positions=[assembly.index(token) for token in order]
        self.assertEqual(positions,sorted(positions))
        for token in (
            "Corrupted Heart step 1",
            "Corrupted Heart step 2",
            "Corrupted Heart step 3",
            "Corrupted Heart step 4",
            "W04_AshenForest",
            "W04_AshenForest_Blockout",
            "W04_Prototype",
        ):
            self.assertIn(token,assembly)

    def test_vertical_slice_names_bone_beast_as_current_completion_boss(self):
        doc=read("docs/W04_ASHEN_FOREST_VERTICAL_SLICE.md")
        self.assertIn(
            "Bone Beast is the final boss/completion gate of the implemented W04 vertical slice",
            doc,
        )
        self.assertIn("Bone Beast defeat — Corrupted Heart step 4/completion",doc)
        self.assertIn("Ash Gate progression — Corrupted Heart step 2",doc)
        self.assertIn("Celestial Wolf bond — Corrupted Heart step 3",doc)

if __name__=="__main__":
    unittest.main()
