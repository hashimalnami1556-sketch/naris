import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


IMPORTER = load('p15_importer', ROOT / 'Unreal/import_and_verify.py')
PREFLIGHT = load('p15_preflight', ROOT / 'Scripts/validate_project.py')
PACKAGE = load('p15_package', ROOT / 'Scripts/verify_package.py')


class StaticMesh:
    def get_class(self):
        return types.SimpleNamespace(get_name=lambda: type(self).__name__)


class SkeletalMesh(StaticMesh):
    def get_editor_property(self, name):
        return self.skeleton


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'Source'
        self.source.mkdir()
        self.report = Path(self.temp.name) / 'new' / 'report.json'
        self.asset = self.source / 'hero.glb'
        self.asset.write_bytes(b'glTF' + b'\x00' * 20)
        self.objects = {}
        self.mode = 'static'
        self.u = types.SimpleNamespace(StaticMesh=StaticMesh, SkeletalMesh=SkeletalMesh,
            AssetImportTask=lambda: types.SimpleNamespace(imported_object_paths=[]), log=lambda _: None,
            load_asset=lambda p: self.objects.get(p))
        self.u.EditorAssetLibrary = types.SimpleNamespace(
            does_directory_exist=lambda _: False, does_asset_exist=lambda p: p in self.objects,
            save_loaded_asset=lambda obj, **kw: True)
        self.u.AssetToolsHelpers = types.SimpleNamespace(get_asset_tools=lambda:
            types.SimpleNamespace(import_asset_tasks=self.import_tasks))

    def import_tasks(self, tasks):
        if self.mode == 'exception':
            raise RuntimeError('Importer failed')
        if self.mode == 'empty':
            return
        for task in tasks:
            path = task.destination_path + '/Hero.Hero'
            if self.mode == 'stale':
                path = '/Game/Old/Hero.Hero'
            obj = SkeletalMesh() if self.mode in ('skeletal', 'no_skeleton') else StaticMesh()
            if isinstance(obj, SkeletalMesh):
                obj.skeleton = None if self.mode == 'no_skeleton' else object()
            self.objects[path] = obj
            task.imported_object_paths = [path]

    def run_import(self, **kw):
        return IMPORTER.execute(self.source, self.report, self.u, run_id='test_run', **kw)

    def assert_failure(self, **kw):
        with self.assertRaises(RuntimeError):
            self.run_import(**kw)
        self.assertFalse(json.loads(self.report.read_text())['verified'])

    def test_static_import(self):
        report = self.run_import()
        self.assertTrue(report['verified'])
        self.assertEqual(report['results'][0]['classes'], ['StaticMesh'])
        self.assertEqual(len(report['results'][0]['sha256']), 64)

    def test_skeletal_import(self):
        self.mode = 'skeletal'
        self.assertTrue(self.run_import()['verified'])

    def test_empty_directory_fails(self):
        self.asset.unlink()
        self.assert_failure()

    def test_missing_source_fails(self):
        self.asset.unlink()
        self.source.rmdir()
        self.assert_failure()

    def test_stale_report_replaced(self):
        self.report.parent.mkdir()
        self.report.write_text('{"verified":true}')
        self.mode = 'empty'
        self.assert_failure()

    def test_no_imported_paths_fails(self):
        self.mode = 'empty'
        self.assert_failure()

    def test_old_asset_paths_fail(self):
        self.mode = 'stale'
        self.assert_failure()

    def test_missing_asset_fails(self):
        self.u.EditorAssetLibrary.does_asset_exist = lambda _: False
        self.assert_failure()

    def test_unloadable_asset_fails(self):
        self.u.load_asset = lambda _: None
        self.assert_failure()

    def test_unsaved_asset_fails(self):
        self.u.EditorAssetLibrary.save_loaded_asset = lambda *a, **kw: False
        self.assert_failure()

    def test_no_skeleton_fails(self):
        self.mode = 'no_skeleton'
        self.assert_failure()

    def test_import_exception_fails(self):
        self.mode = 'exception'
        self.assert_failure()

    def test_existing_destination_fails(self):
        self.u.EditorAssetLibrary.does_directory_exist = lambda _: True
        self.assert_failure()

    def test_invalid_glb_fails(self):
        self.asset.write_bytes(b'bad')
        self.assert_failure()

    def test_spec_requires_animation(self):
        self.assert_failure(spec={'hero.glb': ['SkeletalMesh', 'AnimSequence']})

    def test_spec_rejects_missing_file(self):
        self.assert_failure(spec={'other.glb': []})

    def test_matching_spec_passes(self):
        self.assertTrue(self.run_import(spec={'hero.glb': ['StaticMesh']})['verified'])

    def test_nested_uppercase_glb(self):
        nested = self.source / 'Nested'
        nested.mkdir()
        self.asset.rename(nested / 'hero.GLB')
        self.assertEqual(self.run_import()['results'][0]['source'], 'Nested/hero.GLB')

    def test_duplicate_names_have_distinct_destinations(self):
        nested = self.source / 'Nested'
        nested.mkdir()
        (nested / 'hero.glb').write_bytes(self.asset.read_bytes())
        results = self.run_import()['results']
        self.assertEqual(len(results), 2)
        self.assertNotEqual(results[0]['imported_paths'], results[1]['imported_paths'])

    def test_symlink_escape_fails(self):
        outside = Path(self.temp.name) / 'outside.glb'
        outside.write_bytes(self.asset.read_bytes())
        try:
            (self.source / 'escape.glb').symlink_to(outside)
        except OSError:
            self.skipTest('Symlinks unavailable')
        self.assert_failure()


class ProjectPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'Game/Test.uproject'
        self.project.parent.mkdir()
        self.descriptor = {'Plugins': [{'Name': p, 'Enabled': True} for p in
            ('NarisCombat', 'PythonScriptPlugin', 'EditorScriptingUtilities')]}
        self.write_descriptor()
        self.engine = self.base / 'UE_5.7'
        version = self.engine / 'Engine/Build/Build.version'
        version.parent.mkdir(parents=True)
        version.write_text('{"MajorVersion":5,"MinorVersion":7}')
        self.map = self.project.parent / 'Content/Maps/Test.umap'
        self.map.parent.mkdir(parents=True)
        self.map.write_bytes(b'fixture-map-not-engine-asset')
        target = self.project.parent / 'Source/TestEditor.Target.cs'
        target.parent.mkdir()
        target.write_text('// test fixture')
        self.installed = self.project.parent / 'Plugins/NarisCombat'
        shutil.copytree(ROOT / 'Plugins/NarisCombat', self.installed)

    def write_descriptor(self):
        self.project.write_text(json.dumps(self.descriptor))

    def validate(self, map_path='/Game/Maps/Test'):
        return PREFLIGHT.validate(self.project, self.engine, map_path, ROOT)

    def test_preflight_passes(self):
        self.assertTrue(self.validate()['verified'])

    def test_disabled_plugin_fails(self):
        self.descriptor['Plugins'][0]['Enabled'] = False
        self.write_descriptor()
        with self.assertRaises(ValueError):
            self.validate()

    def test_wrong_engine_fails(self):
        (self.engine / 'Engine/Build/Build.version').write_text('{"MajorVersion":5,"MinorVersion":6}')
        with self.assertRaises(ValueError):
            self.validate()

    def test_changed_installed_plugin_fails(self):
        (self.installed / 'NarisCombat.uplugin').write_text('{}')
        with self.assertRaises(ValueError):
            self.validate()

    def test_old_duplicate_class_fails(self):
        (self.installed / 'Source/NarisCombat/NarisCombatComponent.h').write_text('// old version')
        with self.assertRaises(ValueError):
            self.validate()

    def test_missing_map_fails(self):
        self.map.unlink()
        with self.assertRaises(ValueError):
            self.validate()

    def test_path_traversal_fails(self):
        with self.assertRaises(ValueError):
            self.validate('/Game/../../outside')

    def test_missing_editor_target_fails(self):
        (self.project.parent / 'Source/TestEditor.Target.cs').unlink()
        with self.assertRaises(ValueError):
            self.validate()


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / 'Archive'
        self.exe = self.archive / 'Windows/Test/Binaries/Win64/Test.exe'
        self.exe.parent.mkdir(parents=True)
        self.exe.write_bytes(b'MZ-test-fixture-not-a-runnable-exe')
        self.pak = self.archive / 'Windows/Test/Content/Paks/Test.pak'
        self.pak.parent.mkdir(parents=True)
        self.pak.write_bytes(b'pak-test-fixture')

    def test_expected_artifacts_pass(self):
        report = PACKAGE.verify(self.archive, 'Test')
        self.assertTrue(report['verified'])
        self.assertFalse(report['runtime_tested'])
        self.assertEqual(len(report['artifacts']), 2)
        self.assertTrue(all(len(a['sha256']) == 64 for a in report['artifacts']))

    def test_bootstrap_alone_fails(self):
        self.exe.rename(self.archive / 'Test.exe')
        with self.assertRaises(ValueError):
            PACKAGE.verify(self.archive, 'Test')

    def test_crash_reporter_only_fails(self):
        self.exe.rename(self.exe.with_name('CrashReportClient.exe'))
        with self.assertRaises(ValueError):
            PACKAGE.verify(self.archive, 'Test')

    def test_missing_pak_fails(self):
        self.pak.unlink()
        with self.assertRaises(ValueError):
            PACKAGE.verify(self.archive, 'Test')

    def test_empty_pak_fails(self):
        self.pak.write_bytes(b'')
        with self.assertRaises(ValueError):
            PACKAGE.verify(self.archive, 'Test')

    def test_bad_executable_fails(self):
        self.exe.write_bytes(b'not-an-exe')
        with self.assertRaises(ValueError):
            PACKAGE.verify(self.archive, 'Test')

    def test_named_development_executable_passes(self):
        self.exe.rename(self.exe.with_name('Test-Win64-Development.exe'))
        self.assertTrue(PACKAGE.verify(self.archive, 'Test')['verified'])

    def test_missing_archive_fails(self):
        with self.assertRaises(ValueError):
            PACKAGE.verify(self.archive / 'missing', 'Test')


class CombatRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        compiler = os.environ.get('CXX', shutil.which('g++') or shutil.which('clang++'))
        if not compiler:
            raise RuntimeError('A real C++17 compiler is required; do not silently skip combat tests')
        cls.binary = Path(cls.temp.name) / ('rules.exe' if os.name == 'nt' else 'rules')
        result = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pedantic',
            '-I', str(ROOT / 'Plugins/NarisCombat/Source/NarisCombat/Public'),
            str(ROOT / 'Tests/combat_rules_test.cpp'), '-o', str(cls.binary)],
            capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError('C++ rule compilation failed:\n' + result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()


def make_rule_test(name):
    def test(self):
        result = subprocess.run([str(self.binary), name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    return test


for case in re.findall(r'\{"([a-z_]+)",', (ROOT / 'Tests/combat_rules_test.cpp').read_text()):
    setattr(CombatRulesTests, 'test_' + case, make_rule_test(case))


if __name__ == '__main__':
    unittest.main(verbosity=2)
