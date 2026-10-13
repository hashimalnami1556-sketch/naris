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

    def test_unreal_python_scripts_parse(self):
        for rel in (
            "tools/unreal/p0_03_import_hero.py",
            "tools/unreal/p0_04a_hero_technical_qa.py",
            "tools/unreal/p0_04b_prepare_visual_qa.py",
            "tools/unreal/p0_05_promote_hero.py",
            "tools/unreal/p0_05_rollback_hero.py",
        ):
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
            "material_policy",
            "do not fabricate unassigned style slots",
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
            "output_fbx_sha256",
            "hashlib",
            "import_candidate_ready",
            "pbr_material",
            "material_policy",
            "preserve real assigned PBR",
        ):
            self.assertIn(token, src)

    def test_p0_03_contract(self):
        src = self.read("tools/unreal/p0_03_import_hero.py")
        for token in (
            "P0-03_unreal_hero_import.json",
            "/Game/NARIS/Characters/HeroProduction",
            "FBXIT_SKELETAL_MESH",
            "NARIS.CandidateOnly",
            "baseline_skeleton_reused",
            "create_physics_asset",
            "regenerate_lod",
            "lod_count_at_least_3",
            "P0-04A technical LOD/skeleton/material QA, then P0-04B D3D12 visual/combat QA before swapping HeroV3",
            "SK_AshenVessel_Production.glb",
            "source_format",
            "material_slots_non_null",
            "NARIS.SourceAsset",
            "output_glb_sha256",
            "expected_source_sha256",
            "p0_02_source_sha256_mismatch",
            "p0_02_expected_source_sha256_invalid",
            "diagnostics",
        ):
            self.assertIn(token, src)

    def test_p0_04a_contract(self):
        src = self.read("tools/unreal/p0_04a_hero_technical_qa.py")
        for token in (
            "P0-04A_hero_technical_qa.json",
            "technical_acceptance",
            "visual_acceptance",
            "runtime_combat_acceptance",
            "same_skeleton_as_working_hero",
            "physics_asset",
            "lod_count_at_least_3",
            "compatible_animation_assets",
            "material_slots_non_null",
            "animation_compatible_or_retargeted",
            "do not fabricate unused style slots",
            "replacement_allowed",
            "P0-04B D3D12 visual + deformation + weapon socket + combat regression on AsusRog",
            "candidate_source_sha256",
            "NARIS.SourceSHA256",
        ):
            self.assertIn(token, src)

    def test_p0_04b_contract(self):
        src = self.read("tools/unreal/p0_04b_prepare_visual_qa.py")
        for token in (
            "P0-04B_visual_scene.json",
            "/Game/NARIS/QA/L_HeroCandidate_QA",
            "QA_BASELINE_HeroV3",
            "QA_CANDIDATE_Production",
            "visual_scene_prepared",
            "visual_acceptance",
            "replacement_allowed",
            "P0-05 promotion + packaged combat regression",
        ):
            self.assertIn(token, src)

    def test_p0_04b_render_contract(self):
        src = self.read("tools/unreal/p0_04b_prepare_visual_qa.py")
        for token in (
            "QA_Camera_HeroCompare",
            "auto_activate_for_player",
            "AutoReceiveInput.PLAYER0",
            "P0-04B_HeroCompare.png",
            "replacement_allowed",
        ):
            self.assertIn(token, src)

        workflow = self.read(".github/workflows/p0-hero-self-hosted.yml")
        runner = self.read("tools/windows/Invoke-P0HeroMasterQA.ps1")
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertIn("Invoke-P0HeroMasterQA.ps1", workflow)
        self.assertIn("HighResShot 1", runner)
        self.assertIn('p0-04b-hashbound-camera-v2', runner)
        self.assertIn("P0-04B_render_evidence.json", runner)

    def test_p0_05_promotion_contract(self):
        promote = self.read("tools/unreal/p0_05_promote_hero.py")
        for token in (
            "P0-04B_render_evidence.json",
            "visual_approval_candidate_mismatch",
            "visual_approval_git_sha_mismatch",
            "render_evidence_sha256_mismatch",
            "render_evidence_pipeline_revision_mismatch",
            "visual_approval_pipeline_revision_mismatch",
            "visual_evidence_hash_mismatch",
            "visual_evidence_size_mismatch",
            "render_evidence_candidate_mismatch",
            "render_evidence_baseline_mismatch",
            "render_evidence_map_mismatch",
            "visual_approval_workflow_run_id_mismatch",
            "visual_approval_provenance_missing",
            "skeleton_mismatch_at_promotion",
            "NARIS.VisualEvidenceSHA256",
        ):
            self.assertIn(token, promote)

        approval = self.read("data/P0_HERO_VISUAL_APPROVAL.json")
        for token in (
            '"candidate"',
            '"evidence_git_sha"',
            '"screenshot_sha256"',
            '"pipeline_revision"',
            '"approved": false',
        ):
            self.assertIn(token, approval)

        runner = self.read("tools/windows/run_p0_05_promote_and_regress.bat")
        self.assertIn("Full Cook / Stage / Pak / Archive", runner)
        self.assertNotIn("-iterativecooking", runner)
        self.assertIn("clean_cook_outputs_failed", runner)
        self.assertIn("p0_05_rollback_hero.py", runner)

    def test_p0_05_promotion_and_rollback_contract(self):
        promote = self.read("tools/unreal/p0_05_promote_hero.py")
        rollback = self.read("tools/unreal/p0_05_rollback_hero.py")
        approval = self.read("data/P0_HERO_VISUAL_APPROVAL.json")
        workflow = self.read(".github/workflows/p0-hero-self-hosted.yml")

        for token in (
            "P0-04B_render_evidence.json",
            "screenshot_sha256",
            "screenshot_bytes",
            "visual_approval_criteria_incomplete",
            "visual_evidence_hash_mismatch",
            "visual_evidence_size_mismatch",
            "render_evidence_candidate_mismatch",
            "render_evidence_baseline_mismatch",
            "render_evidence_map_mismatch",
            "visual_approval_workflow_run_id_mismatch",
            "visual_approval_provenance_missing",
            "VisualEvidenceSHA256",
        ):
            self.assertIn(token, promote)

        for token in (
            "RollbackTemp",
            "ACTIVE must never be left empty",
            "active_preserved",
            "archive_restore_failed",
        ):
            self.assertIn(token, rollback)

        for token in (
            '"screenshot_sha256": ""',
            '"screenshot_bytes": 0',
            '"approved_by": ""',
            '"approved_at": ""',
            '"baseline": "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3"',
            '"qa_map": "/Game/NARIS/QA/L_HeroCandidate_QA"',
        ):
            self.assertIn(token, approval)

        runner = self.read("tools/windows/Invoke-P0HeroMasterQA.ps1")
        self.assertIn("P0-04B_render_evidence.json", workflow)
        self.assertIn("Get-FileHash -LiteralPath $ScreenshotOut -Algorithm SHA256", runner)
        self.assertIn("screenshot_bytes = $ScreenshotBytes", runner)
        self.assertIn("workflow_run_id = $WorkflowRunId", runner)
        self.assertIn("name: P0-01 to P0-04B on AsusRog", workflow)

    def test_local_atomic_render_evidence_runner(self):
        src = self.read("tools/windows/run_p0_hero_local_atomic.bat")
        for token in (
            "run_p0_hero_to_unreal.bat",
            "P0-04B_HeroCompare.png",
            "p0-04b-hashbound-camera-v2",
            "Get-FileHash",
            "P0-04B_render_evidence.json",
            "P0-05 promotion remains BLOCKED",
            "del /q \"%SCREEN_DIR%\\*.png\"",
            "RENDER_START",
            "No fresh screenshot produced after render start",
            "git -C $repoRoot rev-parse HEAD",
            "git_worktree_dirty=$dirty",
            "render_started_utc",
            "screenshot_written_utc",
        ):
            self.assertIn(token, src)

    def test_p0_05_self_hosted_workflow_contract(self):
        workflow = self.read(".github/workflows/p0-hero-promote-self-hosted.yml")
        for token in (
            "data/P0_HERO_VISUAL_APPROVAL.json",
            "approval-preflight",
            "needs.approval-preflight.outputs.approved == 'true'",
            "runs-on: [self-hosted, windows]",
            "run_p0_05_promote_and_regress.bat",
            "CALL-OF-NARIS-P0-Hero-Promotion-Evidence",
            "cancel-in-progress: false",
        ):
            self.assertIn(token, workflow)

    def test_p0_04b_and_p0_05_are_hash_bound(self):
        master = self.read("tools/windows/Invoke-P0HeroMasterQA.ps1")
        promote = self.read("tools/unreal/p0_05_promote_hero.py")
        approval = self.read("data/P0_HERO_VISUAL_APPROVAL.json")
        for token in (
            "candidate_source_sha256",
            "P0-04B_runtime_qa.json",
            "PASS_EVIDENCE_READY",
            "technical_runtime_gate",
        ):
            self.assertIn(token, master + promote + approval)
        self.assertIn("candidate_source_sha256_chain_mismatch", promote)

    def test_p0_05_packaged_regression_contract(self):
        src = self.read("tools/windows/run_p0_05_promote_and_regress.bat")
        for token in (
            "PACKAGED_INTERNAL",
            "WaitForExit(120000)",
            "NARIS_COMBAT_QA_RESULT Pass=1",
            "NARIS_HERO_VISUAL_QA MeshVisible=1",
            "Get-FileHash -Algorithm SHA256",
            "qa_log_sha256",
            "packaged_exe_sha256",
            "visual_approval_sha256",
            "promotion_report_sha256",
            "candidate_source_sha256",
            "evidence_git_sha",
            "evidence_workflow_run_id",
            "goto :rollback_runtime",
        ):
            self.assertIn(token, src)

        workflow = self.read(".github/workflows/p0-hero-promote-self-hosted.yml")
        for token in (
            "candidate_source_sha256",
            "/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production",
            "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3",
            "/Game/NARIS/QA/L_HeroCandidate_QA",
            "P0-04B_HeroCompare.png",
        ):
            self.assertIn(token, workflow)

    def test_windows_runners_chain_the_gates(self):
        src = self.read("tools/windows/run_p0_hero_to_unreal.bat")
        for token in (
            "p0_01_hero_oneshot.py",
            "p0_02_hero_rig_pbr.py",
            "p0_03_import_hero.py",
            "p0_04a_hero_technical_qa.py",
            "production_grade",
            "P0-03_unreal_hero_import.json",
            "P0-04A_hero_technical_qa.json",
            "p0_04b_prepare_visual_qa.py",
            "P0-04B_visual_scene.json",
            "P0-04B SCENE READY",
            "Replacement remains BLOCKED until D3D12 screenshot is inspected.",
        ):
            self.assertIn(token, src)

if __name__ == "__main__":
    unittest.main()
