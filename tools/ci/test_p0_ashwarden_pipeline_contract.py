import ast
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]

class AshWardenPipelineContract(unittest.TestCase):
    def read(self,rel):
        p=ROOT/rel
        self.assertTrue(p.is_file(),f"Missing required file: {rel}")
        return p.read_text(encoding="utf-8")

    def test_blender_script_parses_and_is_candidate_only(self):
        rel="tools/blender/p0_boss_ashwarden_oneshot.py"
        src=self.read(rel)
        ast.parse(src,filename=rel)
        for token in (
            "PROCEDURAL_UNIQUE_CANDIDATE",
            "production_grade",
            '"production_grade":False',
            "SK_AshWarden_Candidate.fbx",
            "P0-BOSS_AshWarden_log.json",
            "final_gate",
        ):
            self.assertIn(token,src)

    def test_unreal_import_isolated_candidate(self):
        rel="tools/unreal/p0_boss_02_import_ashwarden.py"
        src=self.read(rel)
        ast.parse(src,filename=rel)
        for token in (
            "/Game/NARIS/Creatures/AshWardenProduction",
            "SK_NARIS_AshWarden_Candidate",
            "candidate_only",
            "NARIS.CandidateOnly",
            "VisualAcceptance",
            "P0-BOSS-03",
        ):
            self.assertIn(token,src)

    def test_runner_does_not_replace_live_proxy(self):
        src=self.read("tools/windows/run_p0_boss_ashwarden_atomic.bat")
        for token in (
            "p0_boss_ashwarden_oneshot.py",
            "p0_boss_02_import_ashwarden.py",
            "PASS CANDIDATE ONLY",
            "Current gameplay boss proxy remains unchanged",
        ):
            self.assertIn(token,src)
        self.assertNotIn("rename_asset",src)

    def test_manifest_blocks_replacement_before_visual_gate(self):
        data=json.loads(self.read("data/P0_ASH_WARDEN_PIPELINE_STATUS.json"))
        self.assertEqual(data["product"],"CALL OF NARIS")
        by_id={s["id"]:s for s in data["stages"]}
        self.assertFalse(by_id["P0-BOSS-02"]["replacement_allowed"])
        self.assertFalse(by_id["P0-BOSS-03"]["replacement_allowed"])
        self.assertEqual(by_id["P0-BOSS-04"]["replacement_allowed"],"only_after_pass")

if __name__=="__main__":
    unittest.main()
