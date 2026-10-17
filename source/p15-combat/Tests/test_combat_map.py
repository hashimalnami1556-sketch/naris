import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('combat_map_gate', ROOT / 'Unreal/validate_combat_map.py')
GATE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GATE)


class Component:
    def __init__(self, issues=None, tag='NarisDamageable'):
        self.issues, self.tag = issues or [], tag

    def get_setup_issues(self):
        return self.issues

    def get_editor_property(self, name):
        assert name == 'damageable_tag'
        return self.tag


class Actor:
    def __init__(self, name, tags, components=None):
        self.name, self.tags = name, tags
        self.components = components if components is not None else [Component()]
        self.damageable = True

    def get_editor_property(self, name):
        return {'tags': self.tags, 'can_be_damaged': self.damageable}[name]

    def get_components_by_class(self, cls):
        return [component for component in self.components if isinstance(component, cls)]

    def get_path_name(self):
        return '/Game/Maps/Test.' + self.name


class CombatMapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.report = Path(self.temp.name) / 'nested' / 'report.json'
        self.hero = Actor('Hero', ['NarisP15Playable'])
        self.target = Actor('Target', ['NarisDamageable'])
        self.actors = [self.hero, self.target]
        self.loads = []
        self.level = types.SimpleNamespace(load_level=self.load_level)
        self.actor_subsystem = types.SimpleNamespace(get_all_level_actors=lambda: self.actors)
        self.u = types.SimpleNamespace(LevelEditorSubsystem=object(), EditorActorSubsystem=object(),
                                       NarisP15CombatComponent=Component, Character=Actor)
        self.u.get_editor_subsystem = lambda cls: self.level if cls == self.u.LevelEditorSubsystem else self.actor_subsystem

    def load_level(self, path):
        self.loads.append(path)
        return True

    def execute(self, path='/Game/Maps/Test'):
        return GATE.execute(path, self.report, self.u, run_id='map_run')

    def assert_failure(self, path='/Game/Maps/Test'):
        with self.assertRaises(RuntimeError):
            self.execute(path)
        self.assertFalse(json.loads(self.report.read_text())['verified'])

    def test_configured_map_passes_as_configuration_only(self):
        report = self.execute()
        self.assertTrue(report['verified'])
        self.assertFalse(report['runtime_tested'])
        self.assertFalse(report['input_wiring_verified'])
        self.assertFalse(report['anim_blueprint_slot_evaluated'])
        self.assertEqual(report['run_id'], 'map_run')
        self.assertEqual(len(report['targets']), 1)

    def test_missing_map_name(self):
        self.assert_failure(None)
        self.assertEqual(self.loads, [])

    def test_map_path_traversal(self):
        self.assert_failure('/Game/../Private')
        self.assertEqual(self.loads, [])

    def test_failed_level_load(self):
        self.level.load_level = lambda _: False
        self.assert_failure()

    def test_empty_map(self):
        self.actors.clear()
        self.assert_failure()

    def test_no_playable_tag(self):
        self.hero.tags.clear()
        self.assert_failure()

    def test_missing_combat_component(self):
        self.hero.components.clear()
        self.assert_failure()

    def test_duplicate_health_owners(self):
        self.hero.components.append(Component())
        self.assert_failure()

    def test_missing_montage_propagates_native_diagnostic(self):
        self.hero.components[0].issues = ['Assign the LightAttack montage.']
        self.assert_failure()
        self.assertIn('LightAttack', str(json.loads(self.report.read_text())['errors']))

    def test_missing_attack_notify_propagates_native_diagnostic(self):
        self.hero.components[0].issues = ['LightAttack needs a positive NARIS P15 Attack Window notify state.']
        self.assert_failure()

    def test_no_target(self):
        self.actors.remove(self.target)
        self.assert_failure()

    def test_player_cannot_target_itself(self):
        self.hero.tags.append('NarisDamageable')
        self.actors.remove(self.target)
        self.assert_failure()

    def test_target_without_health_owner(self):
        self.target.components.clear()
        self.assert_failure()

    def test_target_requires_character_health_owner(self):
        target = self.target
        class Prop:
            def __getattr__(self, name):
                return getattr(target, name)
        self.actors[1] = Prop()
        self.assert_failure()

    def test_mixed_w04_and_p15_hero_health_fails(self):
        class CanonicalComponent:
            pass
        self.u.NarisCombatComponent = CanonicalComponent
        self.hero.components.append(CanonicalComponent())
        self.assert_failure()

    def test_mixed_w04_and_p15_target_health_fails(self):
        class CanonicalComponent:
            pass
        self.u.NarisCombatComponent = CanonicalComponent
        self.target.components.append(CanonicalComponent())
        self.assert_failure()

    def test_damage_disabled_on_target(self):
        self.target.damageable = False
        self.assert_failure()

    def test_custom_damageable_tag(self):
        self.hero.components[0].tag = 'TestHostile'
        self.target.tags = ['TestHostile']
        self.assertTrue(self.execute()['verified'])

    def test_stale_success_report_replaced(self):
        self.report.parent.mkdir()
        self.report.write_text('{"verified":true}')
        self.actors.clear()
        self.assert_failure()

    def test_does_not_change_actor_tags_or_components(self):
        original_tags = list(self.hero.tags), list(self.target.tags)
        original_components = list(self.hero.components), list(self.target.components)
        self.execute()
        self.assertEqual(original_tags, (self.hero.tags, self.target.tags))
        self.assertEqual(original_components, (self.hero.components, self.target.components))

    def test_untagged_actors_do_not_satisfy_target_requirement(self):
        self.target.tags.clear()
        self.assert_failure()
