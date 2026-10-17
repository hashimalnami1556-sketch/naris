"""UE Editor Python entry point. Fails on empty input, stale output or invalid assets."""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import uuid

_source_spec = importlib.util.spec_from_file_location('naris_p15_sources', Path(__file__).with_name('source_assets.py'))
SOURCES = importlib.util.module_from_spec(_source_spec)
_source_spec.loader.exec_module(SOURCES)


def write_report(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def execute(source, report_path, unreal, run_id=None, spec=None):
    source = Path(source).resolve()
    run_id = run_id or uuid.uuid4().hex
    report = {'schema_version': 1, 'run_id': run_id, 'verified': False,
              'scope': 'editor-import-only', 'source': str(source), 'results': []}
    try:
        if not re.fullmatch(r'[A-Za-z0-9_]{1,64}', run_id):
            raise ValueError('Invalid import run ID')
        if not source.is_dir():
            raise ValueError('NARIS_ASSET_DIR is not a directory')
        assets = sorted(p for p in source.rglob('*') if p.is_file() and p.suffix.lower() == '.glb')
        if not assets:
            raise ValueError('No GLB assets found; an empty import cannot pass')
        if any(not p.resolve().is_relative_to(source) for p in assets):
            raise ValueError('Asset symlink escapes the source directory')
        entries = SOURCES.normalize_spec(spec)
        relative_names = {p.relative_to(source).as_posix() for p in assets}
        if entries is not None and set(entries) != relative_names:
            raise ValueError('Import spec must describe every GLB exactly once')
        # فحص جميع الملفات قبل إجراء أي تغيير في مشروع Unreal.
        report['source_checks'] = {
            p.relative_to(source).as_posix(): SOURCES.check_source(p.read_bytes(),
                entries[p.relative_to(source).as_posix()] if entries is not None else None)
            for p in assets}
        destination = '/Game/NARIS/Imported/P15_' + run_id
        report['destination'] = destination
        if unreal.EditorAssetLibrary.does_directory_exist(destination):
            raise ValueError('Run destination exists; choose a fresh run ID')
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        for asset in assets:
            relative = asset.relative_to(source).as_posix()
            result = {'source': relative, 'verified': False, 'imported_paths': []}
            report['results'].append(result)
            try:
                payload = asset.read_bytes()
                result['sha256'] = hashlib.sha256(payload).hexdigest()
                if result['sha256'] != report['source_checks'][relative]['sha256']:
                    raise ValueError('Source changed after the initial validation')
                result['size_bytes'] = len(payload)
                stem = re.sub(r'[^A-Za-z0-9_]', '_', asset.stem)
                suffix = hashlib.sha256(relative.encode()).hexdigest()[:8]
                target = destination + '/' + stem + '_' + suffix
                task = unreal.AssetImportTask()
                task.filename = str(asset)
                task.destination_path = target
                task.automated = True
                task.save = True
                task.replace_existing = False
                tools.import_asset_tasks([task])
                paths = list(task.imported_object_paths)
                result['imported_paths'] = paths
                if not paths or any(not p.startswith(target + '/') for p in paths):
                    raise ValueError('Importer returned no assets or paths outside this run')
                loaded = []
                for path in paths:
                    if not unreal.EditorAssetLibrary.does_asset_exist(path):
                        raise ValueError('Imported object is missing: ' + path)
                    obj = unreal.load_asset(path)
                    if obj is None:
                        raise ValueError('Imported object cannot be loaded: ' + path)
                    if not unreal.EditorAssetLibrary.save_loaded_asset(obj, only_if_is_dirty=False):
                        raise ValueError('Imported object could not be saved: ' + path)
                    loaded.append(obj)
                meshes = [obj for obj in loaded if isinstance(obj, (unreal.StaticMesh, unreal.SkeletalMesh))]
                if not meshes:
                    raise ValueError('No mesh was imported')
                for mesh in meshes:
                    if isinstance(mesh, unreal.SkeletalMesh) and mesh.get_editor_property('skeleton') is None:
                        raise ValueError('Skeletal mesh has no Skeleton')
                result['classes'] = sorted({obj.get_class().get_name() for obj in loaded})
                required = entries[relative]['required_classes'] if entries is not None else []
                if not set(required).issubset(result['classes']):
                    raise ValueError('Missing required classes: ' + repr(set(required) - set(result['classes'])))
                result['verified'] = True
            except Exception as exc:
                result['error'] = str(exc)
            unreal.log(('PASS ' if result['verified'] else 'FAIL ') + relative)
        report['verified'] = bool(report['results']) and all(r['verified'] for r in report['results'])
        if not report['verified']:
            raise RuntimeError('One or more imports failed')
    except Exception as exc:
        report['error'] = str(exc)
        write_report(report_path, report)
        raise RuntimeError(str(exc) + '; see ' + str(report_path)) from exc
    write_report(report_path, report)
    return report


def main():
    report = Path(os.environ.get('NARIS_IMPORT_REPORT', 'naris_import_results.json')).resolve()
    source = os.environ.get('NARIS_ASSET_DIR')
    if not source:
        write_report(report, {'verified': False, 'error': 'NARIS_ASSET_DIR is required'})
        raise RuntimeError('NARIS_ASSET_DIR is required')
    try:
        spec_path = os.environ.get('NARIS_IMPORT_SPEC')
        spec = json.loads(Path(spec_path).read_text(encoding='utf-8-sig')) if spec_path else None
        unreal = importlib.import_module('unreal')
    except Exception as exc:
        write_report(report, {'verified': False, 'error': str(exc)})
        raise
    execute(source, report, unreal, os.environ.get('NARIS_IMPORT_RUN_ID'), spec)


if __name__ == '__main__':
    main()
