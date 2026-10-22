"""Validate the exact source inventory and bind poses before starting Unreal."""
import argparse
import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location('naris_sources', Path(__file__).resolve().parents[1] / 'Unreal/source_assets.py')
SOURCES = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SOURCES)


def verify(directory, contract):
    directory = Path(directory).resolve()
    entries = SOURCES.normalize_spec(contract)
    if entries is None or contract.get('schema_version') != 2:
        raise ValueError('Build preflight requires a version 2 hashed source contract')
    files = sorted(p for p in directory.rglob('*') if p.is_file() and p.suffix.lower() == '.glb')
    if not directory.is_dir() or not files:
        raise ValueError('No source GLBs found')
    if any(not p.resolve().is_relative_to(directory) for p in files):
        raise ValueError('Source symlink escapes asset directory')
    if {p.relative_to(directory).as_posix() for p in files} != set(entries):
        raise ValueError('Source inventory differs from the hashed contract')
    reports = {p.relative_to(directory).as_posix(): SOURCES.check_source(p.read_bytes(), entries[p.relative_to(directory).as_posix()]) for p in files}
    return {'verified': True, 'scope': 'source-intake-only', 'unreal_verified': False, 'assets': reports}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--assets', required=True)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    report = {'verified': False, 'unreal_verified': False}
    try:
        report = verify(args.assets, json.loads(Path(args.spec).read_text(encoding='utf-8-sig')))
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        output = Path(args.report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
