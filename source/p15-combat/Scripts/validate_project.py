"""Read-only build preflight; never copies over an installed plugin or edits a project."""
import argparse
import json
from pathlib import Path
import re


def validate(project, engine, map_path, delivery=None):
    project = Path(project).resolve()
    engine = Path(engine).resolve()
    delivery = Path(delivery or Path(__file__).resolve().parents[1])
    if not project.is_file() or project.suffix.lower() != '.uproject':
        raise ValueError('A real .uproject file is required')
    descriptor = json.loads(project.read_text(encoding='utf-8-sig'))
    version = json.loads((engine / 'Engine/Build/Build.version').read_text(encoding='utf-8-sig'))
    if (version.get('MajorVersion'), version.get('MinorVersion')) != (5, 7):
        raise ValueError('The selected engine must be Unreal 5.7')
    plugins = {p['Name']: p.get('Enabled', False) for p in descriptor.get('Plugins', [])}
    for name in ('NarisCombat', 'PythonScriptPlugin', 'EditorScriptingUtilities'):
        if not plugins.get(name):
            raise ValueError('Project must explicitly enable ' + name)
    installed = project.parent / 'Plugins/NarisCombat'
    supplied = delivery / 'Plugins/NarisCombat'
    for source in supplied.rglob('*'):
        if source.is_file():
            target = installed / source.relative_to(supplied)
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                raise ValueError('Installed plugin differs or is incomplete: ' + str(target))
    expected_sources = {p.relative_to(supplied / 'Source') for p in (supplied / 'Source').rglob('*') if p.is_file()}
    actual_sources = {p.relative_to(installed / 'Source') for p in (installed / 'Source').rglob('*') if p.is_file()}
    if expected_sources != actual_sources:
        raise ValueError('Extra plugin source remains; replace the plugin directory after backing it up')
    if not re.fullmatch(r'/Game/(?:[A-Za-z0-9_]+/)*[A-Za-z0-9_]+', map_path):
        raise ValueError('Map must be a /Game package path without an object suffix')
    map_file = project.parent / 'Content' / (map_path[len('/Game/'):] + '.umap')
    if not map_file.is_file() or map_file.stat().st_size == 0:
        raise ValueError('Cook map does not exist: ' + str(map_file))
    editors = [project.parent / 'Source' / (project.stem + 'Editor.Target.cs')]
    if not editors[0].is_file():
        raise ValueError('Expected Editor target is missing: ' + str(editors[0]))
    return {'project': str(project), 'engine': str(engine), 'editor_target': project.stem + 'Editor',
            'map': map_path, 'verified': True, 'scope': 'read-only-preflight'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--engine', required=True)
    parser.add_argument('--map', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    report = {'verified': False}
    try:
        report = validate(args.project, args.engine, args.map)
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        output = Path(args.report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
