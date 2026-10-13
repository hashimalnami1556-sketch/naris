"""NARIS Fiery Demon: behavior tests with a fake Unreal Editor boundary.

These tests exercise Python orchestration in CI; they do NOT constitute an actual
Unreal 5.7 import, .umap save, animation playback, or PIE combat validation.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

TARGET = Path(__file__).resolve().parents[1] / "unreal" / "import_and_place_fiery_demon.py"

class DummyMesh:
    def __init__(self, name="Demon"):
        self.name = name
    def get_path_name(self):
        return "/Game/NARIS/Enemies/FieryDemon/" + self.name

class DummyAnimation:
    def __init__(self, name):
        self.name = name
    def get_name(self):
        return self.name

class DummyComponent:
    def __init__(self):
        self.mesh = None
        self.animation = None
        self.animation_mode = None
    def set_skeletal_mesh_asset(self, mesh):
        self.mesh = mesh
    def set_animation_mode(self, mode):
        self.animation_mode = mode
    def set_animation(self, animation):
        self.animation = animation

class DummyActor:
    def __init__(self):
        self.label = ""
        self.component = DummyComponent()
    def set_actor_label(self, label):
        self.label = label
    def get_actor_label(self):
        return self.label
    def get_editor_property(self, key):
        assert key == "skeletal_mesh_component", key
        return self.component
    def get_path_name(self):
        return "/Game/NARIS/W04/Maps/L_FieryDemon_QA.PersistentLevel." + self.label

class FakeEditor:
    def __init__(self):
        self.mesh = DummyMesh()
        self.idle = DummyAnimation("NARIS_Beast_Idle")
        self.assets = {
            "/test/Demon": self.mesh,
            "/test/Idle": self.idle,
        }
        self.imported_paths = ["/test/Demon", "/test/Idle"]
        self.import_tasks = []
        self.actors = []
        self.spawn_count = 0
        self.saved_level = 0
        self.saved_asset_directory = 0
        self.levels = set()
        self.current_level = ""
        self.log_errors = []
        self.unreal = types.ModuleType("unreal")
        self.unreal.SkeletalMesh = DummyMesh
        self.unreal.AnimSequence = DummyAnimation
        self.unreal.SkeletalMeshActor = DummyActor
        self.unreal.FBXImportType = types.SimpleNamespace(FBXIT_SKELETAL_MESH="skeletal")
        self.unreal.AnimationMode = types.SimpleNamespace(ANIMATION_SINGLE_NODE="single")
        self.unreal.Vector = lambda *a, **kw: (a, kw)
        self.unreal.Rotator = lambda *a, **kw: (a, kw)
        self.unreal.FbxImportUI = types.SimpleNamespace
        self.unreal.AssetImportTask = types.SimpleNamespace
        self.unreal.AssetToolsHelpers = types.SimpleNamespace(
            get_asset_tools=lambda: types.SimpleNamespace(import_asset_tasks=self.import_asset_tasks))
        self.unreal.EditorAssetLibrary = types.SimpleNamespace(
            save_directory=self.save_assets,
            does_asset_exist=lambda path: path in self.levels)
        self.unreal.EditorLoadingAndSavingUtils = types.SimpleNamespace(load_map=self.load_map)
        self.unreal.EditorLevelLibrary = types.SimpleNamespace(new_level=self.new_level,
                                                                save_current_level=self.save_level)
        self.unreal.EditorActorSubsystem = type("DummySubsystem", (), {})
        self.unreal.get_editor_subsystem = lambda cls: types.SimpleNamespace(
            get_all_level_actors=lambda: self.actors, spawn_actor_from_class=self.spawn)
        self.unreal.load_asset = lambda path: self.assets.get(path)
        self.unreal.log = lambda msg: None
        self.unreal.log_error = self.log_errors.append

    def import_asset_tasks(self, tasks):
        self.import_tasks += tasks
        for task in tasks:
            task.imported_object_paths = list(self.imported_paths)

    def save_assets(self, *args, **kwargs):
        self.saved_asset_directory += 1

    def load_map(self, path):
        if path not in self.levels:
            return False
        self.current_level = path
        self.actors = []
        return True

    def new_level(self, path):
        self.levels.add(path)
        self.current_level = path
        self.actors = []
        return True

    def save_level(self):
        self.saved_level += 1

    def spawn(self, *args):
        self.spawn_count += 1
        actor = DummyActor()
        self.actors.append(actor)
        return actor

class FieryDemonEditorTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeEditor()
        with patch.dict(sys.modules, {"unreal": self.fake.unreal}):
            spec = importlib.util.spec_from_file_location("naris_fiery_demon_tested", TARGET)
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fbx = Path(self.temp.name) / "demon.fbx"
        self.fbx.write_bytes(b"dummy-fbx-fixture; not a real geometry asset")
        self.env = patch.dict(os.environ, {
            "NARIS_DEMON_FBX": str(self.fbx),
            "NARIS_REPORT_JSON": str(Path(self.temp.name) / "result.json"),
        }, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_missing_fbx_stops_before_import_and_map_save(self):
        self.fbx.unlink()
        with self.assertRaisesRegex(RuntimeError, "No skeletal FBX"):
            self.module.main()
        self.assertEqual(len(self.fake.import_tasks), 0)
        self.assertEqual(self.fake.saved_level, 0)

    def test_skeletal_and_animation_import_flags(self):
        mesh, clips, paths = self.module.import_demon(str(self.fbx))
        self.assertIs(mesh, self.fake.mesh)
        self.assertEqual([a.get_name() for a in clips], ["NARIS_Beast_Idle"])
        self.assertEqual(len(paths), 2)
        options = self.fake.import_tasks[0].options
        self.assertTrue(options.import_as_skeletal)
        self.assertTrue(options.import_animations)
        self.assertEqual(options.mesh_type_to_import, "skeletal")

    def test_static_only_asset_is_rejected(self):
        self.fake.imported_paths = ["/test/Idle"]
        with self.assertRaisesRegex(RuntimeError, "SkeletalMesh"):
            self.module.main()
        self.assertEqual(self.fake.saved_level, 0)

    def test_qa_level_created_and_animation_assigned(self):
        report = self.module.main()
        self.assertEqual(report["level"], self.module.QA_LEVEL)
        self.assertEqual(self.fake.current_level, self.module.QA_LEVEL)
        self.assertEqual(self.fake.spawn_count, 1)
        self.assertIs(self.fake.actors[0].component.mesh, self.fake.mesh)
        self.assertIs(self.fake.actors[0].component.animation, self.fake.idle)
        self.assertEqual(self.fake.saved_level, 1)

    def test_same_actor_is_reused_on_reimport(self):
        self.module.main()
        self.module.main()
        self.assertEqual(self.fake.spawn_count, 1)
        self.assertEqual(len(self.fake.actors), 1)

    def test_production_level_requires_explicit_permission(self):
        os.environ["NARIS_ASH_GATE_UMAP"] = "/Game/NARIS/Maps/L_AshGate"
        with self.assertRaisesRegex(RuntimeError, "Refusing to edit production map"):
            self.module.main()
        self.assertEqual(len(self.fake.import_tasks), 0)
        self.assertEqual(self.fake.saved_level, 0)

    def test_nonexistent_production_map_is_never_created(self):
        os.environ["NARIS_ASH_GATE_UMAP"] = "/Game/NARIS/Maps/Nonexistent"
        os.environ["NARIS_ALLOW_MAP_EDIT"] = "1"
        with self.assertRaisesRegex(RuntimeError, "Production level must already exist"):
            self.module.main()
        self.assertEqual(self.fake.saved_level, 0)

    def test_verified_production_map_can_load_with_permission(self):
        path = "/Game/NARIS/Maps/L_AshGate"
        os.environ["NARIS_ASH_GATE_UMAP"] = path
        os.environ["NARIS_ALLOW_MAP_EDIT"] = "1"
        self.fake.levels.add(path)
        report = self.module.main()
        self.assertEqual(report["level"], path)
        self.assertEqual(self.fake.current_level, path)

    def test_no_clips_is_rejected_before_placing_actor(self):
        self.fake.imported_paths = ["/test/Demon"]
        with self.assertRaisesRegex(RuntimeError, "(animation|Animation|clip)"):
            self.module.main()
        self.assertEqual(self.fake.spawn_count, 0)
        self.assertEqual(self.fake.saved_level, 0)

    def test_report_does_not_invent_combat_or_pie_results(self):
        report = self.module.main()
        saved = json.loads((Path(self.temp.name) / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(saved, report)
        self.assertFalse(report["boss_ai_active"])
        self.assertFalse(report["combat_validated"])
        self.assertFalse(report["pie_tested"])
        self.assertFalse(report["shipping_approved"])

if __name__ == "__main__":
    unittest.main()
