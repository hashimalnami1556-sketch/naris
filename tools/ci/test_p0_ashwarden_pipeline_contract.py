import ast
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]

class AshWardenProductionPipelineContract(unittest.TestCase):
    def read(self,rel):
        p=ROOT/rel
        self.assertTrue(p.is_file(),f"Missing Ash Warden pipeline file: {rel}")
        return p.read_text(encoding="utf-8")

    def test_python_scripts_parse(self):
        for rel in (
            "tools/blender/p0_boss_ashwarden_oneshot.py",
            "tools/blender/p0_boss_02_rig_anim_pbr.py",
            "tools/unreal/p0_boss_03_import_qa.py",
        ):
            ast.parse(self.read(rel),filename=rel)

    def test_boss_01_stays_candidate_only(self):
        src=self.read("tools/blender/p0_boss_ashwarden_oneshot.py")
        for token in (
            "PASS_CANDIDATE",
            "production_grade",
            "PROCEDURAL_UNIQUE_CANDIDATE",
            "never reuses BoneBeast as final art",
            "P0-BOSS_AshWarden_log.json",
        ):
            self.assertIn(token,src)
        self.assertIn('"production_grade":False',src)

    def test_boss_02_requires_rig_six_actions_and_pbr(self):
        src=self.read("tools/blender/p0_boss_02_rig_anim_pbr.py")
        for token in (
            "P0-BOSS-02_rig_anim_pbr.json",
            "A_AshWarden_Idle",
            "A_AshWarden_Walk",
            "A_AshWarden_Attack",
            "A_AshWarden_Phase2",
            "A_AshWarden_HitReact",
            "A_AshWarden_Death",
            "M_AshWarden_BlackenedSteel",
            "M_AshWarden_AgedBronze",
            "M_AshWarden_Burgundy",
            "M_AshWarden_Ember",
            "canonical_required_at_least_9",
            "weighted_body_mesh",
            "six_actions",
            "four_pbr_materials",
        ):
            self.assertIn(token,src)

    def test_boss_03_requires_unreal_runtime_assets_and_qa_map(self):
        src=self.read("tools/unreal/p0_boss_03_import_qa.py")
        for token in (
            "P0-BOSS-03_unreal_qa.json",
            "/Game/NARIS/Creatures/AshWardenProduction",
            "/Game/NARIS/QA/L_AshWardenCandidate_QA",
            "create_physics_asset",
            "lod_count_at_least_3",
            "material_slots_at_least_4",
            "idle_animation",
            "walk_animation",
            "attack_animation",
            "phase2_animation",
            "hitreact_animation",
            "death_animation",
            "QA_PROXY_BoneBeast",
            "QA_ASHWARDEN_Idle",
            "QA_ASHWARDEN_Phase2",
            "replacement_allowed",
        ):
            self.assertIn(token,src)

    def test_atomic_runner_chains_all_pre_replacement_gates(self):
        src=self.read("tools/windows/run_p0_boss_ashwarden_atomic.bat")
        for token in (
            "p0_boss_ashwarden_oneshot.py",
            "p0_boss_02_rig_anim_pbr.py",
            "p0_boss_03_import_qa.py",
            "P0-BOSS-02_rig_anim_pbr.json",
            "P0-BOSS-03_unreal_qa.json",
            "production_candidate",
            "technical_acceptance",
            "replacement_allowed",
            "P0-BOSS-04 remains BLOCKED",
        ):
            self.assertIn(token,src)
        self.assertNotIn("rename_asset",src)

    def test_manifest_matches_pipeline_and_blocks_replacement(self):
        data=json.loads(self.read("data/P0_ASH_WARDEN_PIPELINE_STATUS.json"))
        self.assertEqual(data["product"],"CALL OF NARIS")
        stages={s["id"]:s for s in data["stages"]}
        self.assertEqual(
            stages["P0-BOSS-02"]["script"],
            "tools/blender/p0_boss_02_rig_anim_pbr.py"
        )
        self.assertEqual(
            stages["P0-BOSS-03"]["script"],
            "tools/unreal/p0_boss_03_import_qa.py"
        )
        self.assertFalse(stages["P0-BOSS-01"]["replacement_allowed"])
        self.assertFalse(stages["P0-BOSS-02"]["replacement_allowed"])
        self.assertFalse(stages["P0-BOSS-03"]["replacement_allowed"])
        self.assertEqual(
            stages["P0-BOSS-04"]["replacement_allowed"],
            "only_after_pass"
        )
        self.assertIn("packaged",stages["P0-BOSS-04"]["gate"].lower())
        self.assertIn("rollback",stages["P0-BOSS-04"]["gate"].lower())

if __name__=="__main__":
    unittest.main()
