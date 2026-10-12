#!/usr/bin/env python3
"""Install the approved NARSIC loading artwork into an existing Unreal project.

The full-quality PNG is supplied with the conversation delivery bundle, not
embedded into this UTF-8 repository script. Supports NARIS_W04 and NARIS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

APPROVED_SHA256 = "5e5716b02c2641948d93b481444ab6ecd2350318b0e3d63290801a9b2cde90d0"
STAGE = '+DirectoriesToAlwaysStageAsNonUFS=(Path="NARSIC/Loading")'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--code-template", type=Path, default=Path(__file__).resolve().parents[1]
        / "unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.cpp")
    parser.add_argument("--assets-only", action="store_true")
    args = parser.parse_args()

    project_root = args.project.resolve()
    candidates = sorted(project_root.glob("*.uproject"))
    if not candidates:
        raise SystemExit("No .uproject found at project root")
    document = json.loads(candidates[0].read_text(encoding="utf-8-sig"))
    runtime_modules = [m["Name"] for m in document.get("Modules", [])
        if m.get("Type") == "Runtime"]
    if not runtime_modules:
        raise SystemExit("No runtime module")
    name = runtime_modules[0]
    source = args.image.resolve()
    if hashlib.sha256(source.read_bytes()).hexdigest() != APPROVED_SHA256:
        raise SystemExit("Art SHA mismatch. Refusing an unapproved replacement.")

    dest = project_root / "Content/NARSIC/Loading/NARSIC_Transit_Approved.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.is_file() or dest.read_bytes() != source.read_bytes():
        shutil.copyfile(source, dest)

    if not args.assets_only:
        template = args.code_template.read_text(encoding="utf-8")
        source_cpp = project_root / "Source" / name / (name + ".cpp")
        build_file = project_root / "Source" / name / (name + ".Build.cs")
        if not source_cpp.is_file() or not build_file.is_file():
            raise SystemExit("Module source or Build.cs missing")
        old = source_cpp.read_text(encoding="utf-8-sig")
        if "IMPLEMENT_PRIMARY_GAME_MODULE(" not in old:
            raise SystemExit("Unexpected module layout, refusing overwrite")
        if len(old) > 1400 and "FNarsicGameModule" not in old:
            raise SystemExit("Custom module code: integrate manually or use --assets-only")

        new_cpp = template.replace("NARIS_W04", name)
        if old != new_cpp:
            shutil.copyfile(source_cpp, source_cpp.with_suffix(".cpp.pre_narsic"))
            source_cpp.write_text(new_cpp, encoding="utf-8")
        existing = build_file.read_text(encoding="utf-8-sig")
        if '"MoviePlayer"' not in existing:
            changed, count = re.subn(
                r'(PublicDependencyModuleNames\\.AddRange\\(new string\\[\\]\\s*\\{)',
                r'\\1 "MoviePlayer",', existing, count=1,
            )
            if count != 1:
                raise SystemExit("Cannot patch Build.cs automatically")
            build_file.write_text(changed, encoding="utf-8")

    config_file = project_root / "Config/DefaultGame.ini"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    original = config_file.read_text(encoding="utf-8-sig") if config_file.exists() else ""
    if STAGE not in original:
        config_file.write_text(
            original + "\\n[/Script/UnrealEd.ProjectPackagingSettings]\\n" + STAGE + "\\n",
            encoding="utf-8"
        )

    print("NARSIC transit art staged:", dest)
    print("Compile the module; package and perform visible manual QA on Win64.")


if __name__ == "__main__":
    main()
