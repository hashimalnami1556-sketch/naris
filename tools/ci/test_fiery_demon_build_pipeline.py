"""End-to-end build *contract* for the Fiery Demon QA vertical slice.

Runs in GitHub-hosted Python CI; no Blender/Unreal/Windows execution is implied.
"""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
POWERSHELL = ROOT / "tools/windows/Invoke-NarisFieryDemonBuild.ps1"
BLENDER = ROOT / "tools/blender/export_naris_fiery_demon.py"
IMPORTER = ROOT / "tools/unreal/import_fiery_demon_runtime.py"
README = ROOT / "docs/production/NARIS_FIERY_DEMON_RUNTIME_GATE.md"

class FieryDemonBuildPipelineContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ps = POWERSHELL.read_text(encoding="utf-8")
        cls.blender = BLENDER.read_text(encoding="utf-8")
        cls.importer = IMPORTER.read_text(encoding="utf-8")
        cls.docs = README.read_text(encoding="utf-8")

    def test_blender_exporter_is_valid_python(self):
        ast.parse(self.blender)

    def test_blender_refuses_animationless_or_skinless_export(self):
        for token in ('"ARMATURE"', '"MESH"', 'bpy.data.actions',
                      'RuntimeError', 'bpy.ops.import_scene.gltf',
                      'bpy.ops.export_scene.fbx'):
            self.assertIn(token, self.blender)

    def test_export_contains_actions_and_no_leaf_bones(self):
        for token in ('bake_anim_use_all_actions=True', 'add_leaf_bones=False',
                      'use_selection=True'):
            self.assertIn(token, self.blender)

    def test_windows_build_gates_on_input_asset_and_engine(self):
        for token in ("[string]$DemonGlb", "Assert-File $DemonGlb", "Test-Path -LiteralPath $Path -PathType Leaf",
                      "UnrealEditor-Cmd.exe", "RunUAT.bat", "Build.bat"):
            self.assertIn(token, self.ps)

    def test_windows_native_compile_precedes_editor_import(self):
        self.assertLess(self.ps.index('NARIS_W04Editor'), self.ps.index('-ExecutePythonScript'))

    def test_windows_requires_real_unreal_import_report(self):
        for token in ("NARIS_REPORT_JSON", "ConvertFrom-Json", "editor_map_saved",
                      "animations_imported", "L_FieryDemon_QA.umap"):
            self.assertIn(token, self.ps)

    def test_windows_package_explicit_qa_level(self):
        for token in ('-map=L_FieryDemon_QA', 'L_FieryDemon_QA',
                      'NARIS_W04.exe', '-archive'):
            self.assertIn(token, self.ps)

    def test_windows_run_is_opt_in(self):
        for token in ('[switch]$Package', '[switch]$Launch',
                      'Start-Process', 'WaitForExit', 'Get-ChildItem'):
            self.assertIn(token, self.ps)

    def test_windows_does_not_kill_running_unreal_editor(self):
        self.assertIn('Get-Process -Name UnrealEditor', self.ps)
        self.assertIn('throw', self.ps)

    def test_one_click_launcher_uses_fresh_build_and_user_assets(self):
        launcher = (ROOT / "tools/windows/RUN_NARIS_FIERY_DEMON.cmd").read_text(encoding="utf-8")
        self.assertIn("Invoke-NarisFieryDemonBuild.ps1",launcher)
        self.assertIn("NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb",launcher)
        self.assertIn("-Package -Launch",launcher)
        self.assertIn("if exist",launcher)
        self.assertIn("exit /b",launcher)

    def test_localization_is_built_before_cooking(self):
        self.assertIn("Invoke-NarisLocalization.ps1", self.ps)
        self.assertLess(self.ps.index("Invoke-NarisLocalization.ps1"),
                        self.ps.index('"BuildCookRun"'))

    def test_launch_can_keep_game_running_after_success(self):
        self.assertIn("[switch]$SmokeOnly", self.ps)
        self.assertIn("if ($SmokeOnly -or -not $smokeAccepted)", self.ps)

    def test_new_qa_archive_isolated_by_timestamp(self):
        self.assertIn('ToString("yyyyMMdd_HHmmss")', self.ps)

    def test_importer_keeps_production_edit_guard(self):
        self.assertIn('NARIS_ALLOW_MAP_EDIT', self.importer)
        self.assertIn('NARIS_TARGET_MAP', self.importer)
        self.assertIn('"pie_tested":False', self.importer)

    def test_docs_distinguish_ci_from_unreal_execution(self):
        for token in ('BuildCookRun', 'PIE', 'GitHub Actions',
                      'AsusRog', 'FieryDemon'):
            self.assertIn(token, self.docs)

if __name__=="__main__":
    unittest.main()
