import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class HeroProductionPipelineContract(unittest.TestCase):
    def read(self, rel):
        p = ROOT / rel
        self.assertTrue(p.is_file(), f"Missing required pipeline file: {rel}")
        return p.read_text(encoding="utf-8")

    def test_blender_python_scripts_parse(self):
        for rel in (
            "tools/blender/p0_01_hero_oneshot.py",
            "tools/blender/p0_02_hero_rig_pbr.py",
        ):
            src = self.read(rel)
            ast.parse(src, filename=rel)

    def test_unreal_python_script_parses(self):
        rel = "tools/unreal/p0_03_import_hero.py"
        src = self.read(rel)
        ast.parse(src, filename=rel)

    def test_p0_01_contract(self):
        src = self.read("tools/blender/p0_01_hero_oneshot.py")
        for token in (
            "P0-01_reimport_log.json",
            '"production_grade"',
            "OK_PRODUCTION_FROM_",
            "EMERGENCY_2_5D_RELIEF_FROM_",
            "armatures",
            "humanoid_bone_hits",
            "SK_AshenVessel_Production.fbx",
        ):
            self.assertIn(token, src)

    def test_p0_02_contract(self):
        src = self.read("tools/blender/p0_02_hero_rig_pbr.py")
        for token in (
            "P0-02_rig_pbr_log.json",
            "p0_01_not_production_grade",
            "canonical_required",
            "weighted_mesh",
            "M_NARIS_Obsidian",
            "M_NARIS_AgedGold",
            "M_NARIS_EmberFire",
            "SK_AshenVessel_PBR.fbx",
        ):
            self.assertIn(token, src)

    def test_p0_03_contract(self):
        src = self.read("tools/unreal/p0_03_import_hero.py")
        for token in (
            "P0-03_unreal_hero_import.json",
            "/Game/NARIS/Characters/HeroProduction",
            "FBXIT_SKELETAL_MESH",
            "NARIS.CandidateOnly",
            "P0-04 Runtime visual/combat QA before swapping HeroV3",
        ):
            self.assertIn(token, src)

    def test_windows_runners_chain_the_gates(self):
        src = self.read("tools/windows/run_p0_hero_to_unreal.bat")
        for token in (
            "p0_01_hero_oneshot.py",
            "p0_02_hero_rig_pbr.py",
            "p0_03_import_hero.py",
            "production_grade",
            "P0-03_unreal_hero_import.json",
        ):
            self.assertIn(token, src)

if __name__ == "__main__":
    unittest.main()
