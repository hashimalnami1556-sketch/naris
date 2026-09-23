"""Static bootstrap checks; these do not replace UnrealBuildTool or an editor test."""
from collections import defaultdict
from pathlib import Path
import re


def validate_source(source: Path) -> list[str]:
    errors = []
    if not source.is_dir():
        return [f"Missing Unreal Source directory: {source}"]
    targets = defaultdict(list)
    modules = defaultdict(list)
    reflected_enums = defaultdict(list)
    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        if path.suffix not in {'.cs', '.cpp', '.h'}:
            continue
        text = path.read_text(encoding='utf-8')
        if not text.strip():
            errors.append(f"Empty Unreal source: {path.relative_to(source)}")
        # Ignore comments so retired examples do not count as declarations.
        text = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
        if path.name.endswith('.Target.cs'):
            for name in re.findall(r'\bclass\s+(\w+)\s*:\s*TargetRules\b', text):
                targets[name].append(path.relative_to(source))
        for name in re.findall(
            r'\bUENUM\s*\([^)]*\)\s*enum\s+class\s+(\w+)\b',
            text,
            flags=re.S
        ):
            reflected_enums[name].append(path.relative_to(source))
        if path.suffix == '.cpp':
            for name in re.findall(
                r'\bIMPLEMENT_(?:PRIMARY_GAME_MODULE|GAME_MODULE|MODULE)\s*\(\s*\w+\s*,\s*(\w+)', text
            ):
                modules[name].append(path.relative_to(source))
    for name in ('NARIS_W04Target', 'NARIS_W04EditorTarget'):
        if len(targets[name]) != 1:
            errors.append(f"Expected one {name} definition; found {len(targets[name])}: {targets[name]}")
    if len(modules['NARIS_W04']) != 1:
        errors.append(f"Expected one NARIS_W04 module registration; found {len(modules['NARIS_W04'])}: {modules['NARIS_W04']}")
    for name, paths in sorted(reflected_enums.items()):
        if len(paths) > 1:
            errors.append(f"Duplicate reflected enum {name}: {paths}")
    return errors
