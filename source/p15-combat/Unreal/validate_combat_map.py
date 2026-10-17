"""Read-only Editor configuration gate, deliberately separate from a gameplay test."""
import importlib
import json
import os
from pathlib import Path
import re
import uuid


def execute(map_path, report_path, unreal, run_id=None):
    report = {'schema_version': 1, 'run_id': run_id or uuid.uuid4().hex,
              'map': map_path, 'verified': False, 'scope': 'editor-combat-configuration-only',
              'runtime_tested': False, 'input_wiring_verified': False,
              'anim_blueprint_slot_evaluated': False, 'playable_actors': [], 'targets': [], 'errors': []}
    try:
        if not isinstance(map_path, str) or not re.fullmatch(r'/Game/(?:[A-Za-z0-9_]+/)*[A-Za-z0-9_]+', map_path):
            raise ValueError('A valid /Game map package path is required')
        if not re.fullmatch(r'[A-Za-z0-9_]{1,64}', report['run_id']):
            raise ValueError('Invalid map-gate run ID')
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        if not levels.load_level(map_path):
            raise ValueError('Could not load the requested combat map')
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actors = list(actor_subsystem.get_all_level_actors())
        if not actors:
            raise ValueError('Combat map contains no loaded actors')
        # Never create, save, retag or repair actors in a validation pass.
        for actor in actors:
            tags = {str(tag) for tag in actor.get_editor_property('tags')}
            components = list(actor.get_components_by_class(unreal.NarisP15CombatComponent))
            if 'NarisP15Playable' not in tags:
                continue
            record = {'actor': actor.get_path_name(), 'issues': []}
            report['playable_actors'].append(record)
            canonical = getattr(unreal, 'NarisCombatComponent', None)
            if canonical is not None and actor.get_components_by_class(canonical):
                record['issues'].append('Do not attach both W04 and P15 health owners')
            if len(components) != 1:
                record['issues'].append('Exactly one NarisP15CombatComponent is required')
                continue
            record['issues'].extend(str(issue) for issue in components[0].get_setup_issues())
            record['damageable_tag'] = str(components[0].get_editor_property('damageable_tag'))
            candidates = []
            for target in actors:
                if target == actor:
                    continue
                target_tags = {str(tag) for tag in target.get_editor_property('tags')}
                if record['damageable_tag'] not in target_tags:
                    continue
                target_components = list(target.get_components_by_class(unreal.NarisP15CombatComponent))
                if not isinstance(target, unreal.Character):
                    record['issues'].append('P15 health target must be a Character: ' + target.get_path_name())
                elif canonical is not None and target.get_components_by_class(canonical):
                    record['issues'].append('Target has both W04 and P15 health owners: ' + target.get_path_name())
                elif len(target_components) != 1:
                    record['issues'].append('Target needs one P15 health owner: ' + target.get_path_name())
                elif not target.get_editor_property('can_be_damaged'):
                    record['issues'].append('Target damage reception is disabled: ' + target.get_path_name())
                else:
                    candidates.append(target.get_path_name())
            if not candidates:
                record['issues'].append('No damageable P15 target is configured for this actor')
            report['targets'].extend(candidates)
        report['targets'] = sorted(set(report['targets']))
        if not report['playable_actors']:
            report['errors'].append('Tag a placed test Character NarisP15Playable')
        for record in report['playable_actors']:
            report['errors'].extend(record['actor'] + ': ' + issue for issue in record['issues'])
        report['verified'] = bool(report['playable_actors']) and bool(report['targets']) and not report['errors']
        if not report['verified']:
            raise ValueError('Combat-map configuration failed')
    except Exception as exc:
        report['errors'].append(str(exc))
        write_report(report_path, report)
        raise RuntimeError(str(exc) + '; see ' + str(report_path)) from exc
    write_report(report_path, report)
    return report


def write_report(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main():
    report = os.environ.get('NARIS_COMBAT_REPORT', 'combat_map_report.json')
    try:
        unreal = importlib.import_module('unreal')
    except Exception as exc:
        write_report(report, {'verified': False, 'runtime_tested': False, 'errors': [str(exc)]})
        raise
    return execute(os.environ.get('NARIS_COMBAT_MAP'), report, unreal,
                   os.environ.get('NARIS_COMBAT_RUN_ID'))


if __name__ == '__main__':
    main()
