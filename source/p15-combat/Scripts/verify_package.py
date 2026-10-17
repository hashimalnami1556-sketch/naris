"""Check fresh UAT output without treating an EXE's existence as a playtest."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def verify(root, project_name):
    root = Path(root).resolve()
    if not re.fullmatch(r'[A-Za-z0-9_]+', project_name):
        raise ValueError('Invalid project name')
    if not root.is_dir():
        raise ValueError('UAT archive directory is missing')
    executables = []
    packages = []
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(root):
            raise ValueError('Packaged file escapes the archive directory')
        relative = path.relative_to(root).as_posix()
        if path.name in (project_name + '.exe', project_name + '-Win64-Development.exe'):
            if path.parent.name == 'Win64' and path.parent.parent.name == 'Binaries':
                with path.open('rb') as stream:
                    if stream.read(2) != b'MZ':
                        raise ValueError('Packaged game executable has no Windows header')
                executables.append(path)
        if path.suffix.lower() == '.pak' and '/Content/Paks/' in '/' + relative and path.stat().st_size > 0:
            packages.append(path)
    if not executables:
        raise ValueError('No nonempty project game executable under Binaries/Win64')
    if not packages:
        raise ValueError('No nonempty cooked PAK under Content/Paks')
    records = []
    for path in sorted(executables + packages):
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        records.append({'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
                        'sha256': digest.hexdigest()})
    return {'verified': True, 'scope': 'package-artifacts-only', 'runtime_tested': False, 'artifacts': records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True)
    parser.add_argument('--project-name', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    report = {'verified': False, 'runtime_tested': False}
    try:
        report = verify(args.archive, args.project_name)
    except Exception as exc:
        report['error'] = str(exc)
        raise
    finally:
        output = Path(args.report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
