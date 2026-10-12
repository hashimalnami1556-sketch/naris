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
            "tools/unreal/p0_boss_04_discover_integration.py",
            "tools/ci/p0_boss_04_decide_promotion.py",
            "tools/ci/p0_boss_04_patch_native_source.py",
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

    def test_boss_render_evidence_and_visual_approval_gate(self):
        runner=self.read("tools/windows/run_p0_boss_03_local_visual.bat")
        approval=self.read("data/P0_ASH_WARDEN_VISUAL_APPROVAL.json")

        for token in (
            "del /q \"%SCREEN_DIR%\\*.png\"",
            "RENDER_START",
            "No fresh Ash Warden screenshot produced after render start",
            "Get-FileHash -LiteralPath $canonical -Algorithm SHA256",
            "screenshot_sha256=$hash",
            "screenshot_bytes=$bytes",
            "git -C $repoRoot rev-parse HEAD",
            "git_worktree_dirty=$dirty",
            "P0-BOSS-03_render_evidence.json",
            "P0-BOSS-04 replacement remains BLOCKED",
        ):
            self.assertIn(token,runner)

        for token in (
            '"approved": false',
            '"decision": "PENDING_VISUAL_INSPECTION"',
            '"replacement_allowed": false',
            '"screenshot_sha256": ""',
            '"screenshot_bytes": 0',
            '"silhouette_unique_vs_proxy": "pending"',
            '"deformation_attack": "pending"',
            '"deformation_phase2": "pending"',
            '"deformation_death": "pending"',
            '"weapon_readability": "pending"',
            '"boss_readability_at_camera_distance": "pending"',
        ):
            self.assertIn(token,approval)

    def test_boss_04_discovery_is_read_only(self):
        src=self.read("tools/unreal/p0_boss_04_discover_integration.py")
        runner=self.read("tools/windows/run_p0_boss_04_discovery.bat")

        ast.parse(src,filename="tools/unreal/p0_boss_04_discover_integration.py")
        for token in (
            "P0-BOSS-04_integration_discovery.json",
            "read_only",
            "replacement_allowed",
            "bonebeast_proxy_confirmed",
            "native_skeletal_component",
            "recommended_integration_strategy",
            "VERIFY_LOCAL_CXX_DEFAULT_OR_BEGINPLAY_BEFORE_OVERRIDE",
        ):
            self.assertIn(token,src)

        for forbidden in (
            "rename_asset(",
            "save_current_level(",
            "save_dirty_packages(",
            "set_skeletal_mesh_asset(",
            "set_editor_property(\"skeletal_mesh\"",
        ):
            self.assertNotIn(forbidden,src)

        for token in (
            "p0_boss_04_discover_integration.py",
            "READ ONLY",
            "replacement_allowed",
            "P0-BOSS-04 promotion remains BLOCKED",
        ):
            self.assertIn(token,runner)


    def test_boss_04_native_source_is_fingerprinted_and_reversible(self):
        discovery=self.read("tools/unreal/p0_boss_04_discover_integration.py")
        decision=self.read("tools/ci/p0_boss_04_decide_promotion.py")
        patch=self.read("tools/ci/p0_boss_04_patch_native_source.py")
        runner=self.read("tools/windows/run_p0_boss_04_promote_and_regress.bat")

        for token in (
            "source_evidence",
            "cpp_sha256",
            "ashwarden_constructor_sha256",
            "bonebeast_paths_in_constructor",
            "ANarisAshWarden::ANarisAshWarden()",
        ):
            self.assertIn(token,discovery)

        for token in (
            "READY_NATIVE_CXX_PATCH",
            "native_source_errors",
            "constructor_sha256_invalid",
            "bonebeast_proxy_paths_not_found_in_constructor",
            "runtime_bonebeast_proxy_not_confirmed",
        ):
            self.assertIn(token,decision)

        for token in (
            "source_cpp_sha256_changed_since_discovery",
            "constructor_sha256_changed_since_discovery",
            "constructor_proxy_roles_incomplete",
            "NARIS_BOSS_ART_READY",
            "before_cpp_sha256",
            "after_cpp_sha256",
            "--mode",
            "rollback",
            "rollback_refused_source_changed_after_patch",
        ):
            self.assertIn(token,patch)

        for token in (
            "READY_NATIVE_CXX_PATCH",
            "NARIS Win64 Development",
            "NARIS_BOSS_ART_READY Mesh=SK_NARIS_AshWarden_Production",
            "NARIS_BOSS_QA Spawned=1",
            "NARIS_BOSS_PHASE2",
            "NARIS_COMBAT_QA_RESULT Pass=1",
            "Full Cook / Stage / Pak / Archive",
            "--mode rollback",
            "Restoring clean packaged baseline",
        ):
            self.assertIn(token,runner)
        self.assertNotIn("-iterativecooking",runner)

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
            "only_after_pass_and_discovery"
        )
        self.assertIn(
            "P0-BOSS-04 integration discovery report",
            stages["P0-BOSS-04"]["prerequisites"]
        )
        self.assertIn("packaged",stages["P0-BOSS-04"]["gate"].lower())
        self.assertIn("rollback",stages["P0-BOSS-04"]["gate"].lower())

if __name__=="__main__":
    unittest.main()
