from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    ROOT / "README.md",
    ROOT / "NARIS_MASTER",
    ROOT / "docs",
    ROOT / "data",
    ROOT / "worlds",
    ROOT / "unreal" / "NARIS_W04" / "NARIS_W04.uproject",
]

errors: list[str] = []
for path in REQUIRED:
    if not path.exists():
        errors.append(f"Missing required path: {path.relative_to(ROOT)}")

json_count = 0
for path in ROOT.rglob("*.json"):
    if any(part in {"node_modules", ".git", "Binaries", "Intermediate", "Saved", "DerivedDataCache"} for part in path.parts):
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
        json_count += 1
    except Exception as exc:
        errors.append(f"Invalid JSON: {path.relative_to(ROOT)} ({exc})")

uproject = ROOT / "unreal" / "NARIS_W04" / "NARIS_W04.uproject"
if uproject.exists():
    try:
        data = json.loads(uproject.read_text(encoding="utf-8"))
        if "FileVersion" not in data:
            errors.append("Unreal project does not contain FileVersion")
    except Exception as exc:
        errors.append(f"Invalid Unreal .uproject: {exc}")

if errors:
    print("NARIS CI validation FAILED")
    for error in errors:
        print(f"::error::{error}")
    sys.exit(1)

print("NARIS CI validation PASSED")
print(f"Validated JSON files: {json_count}")
print("Validated Unreal project: unreal/NARIS_W04/NARIS_W04.uproject")
