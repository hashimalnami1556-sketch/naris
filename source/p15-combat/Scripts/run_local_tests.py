"""Produce reproducible local evidence, with explicit engine/runtime boundaries."""
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
reports = ROOT / 'Reports'
reports.mkdir(exist_ok=True)
command = [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'Tests'), '-v']
result = subprocess.run(command, text=True, capture_output=True)
output = result.stdout + result.stderr
(reports / 'local_tests.txt').write_text(output, encoding='utf-8')
compiler = os.environ.get('CXX', shutil.which('g++') or shutil.which('clang++'))
compiler_version = subprocess.run([compiler, '--version'], capture_output=True, text=True).stdout.splitlines()[0] if compiler else None
report = {'scope': 'portable-rules-and-mocked-editor-io', 'exit_code': result.returncode,
          'python': platform.python_version(), 'compiler': compiler_version,
          'unreal_compiled': False, 'unreal_import_executed': False,
          'powershell_executed_locally': False, 'windows_packaged': False,
          'gameplay_playtested': False}
match = re.search(r'Ran (\d+) tests?', output)
report['tests_run'] = int(match.group(1)) if match else 0
report['groups'] = {group: len(re.findall(r'\(test_(?:delivery|source_assets|combat_map)\.' + group + r'\.', output))
                    for group in ('CombatRulesTests', 'ImportTests', 'ProjectPreflightTests', 'PackageTests',
                                  'SourceAssetTests', 'SourceContractTests', 'CombatMapTests')}
(reports / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(output, end='')
raise SystemExit(result.returncode)
