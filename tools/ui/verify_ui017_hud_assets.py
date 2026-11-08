"""UI-017 — read-only in-editor native icon audit (Unreal Engine 5.7).

The editor must compile project C++ and load six original SHA256-pinned PNG
exports as Texture2D assets via UI-016 first. This tool neither mutates maps
nor claims to have rendered them: it only proves imported assets are present.
Run with UnrealEditor-Cmd.exe <uproject> -ExecutePythonScript=<this file>
Set NARIS_UI017_AUDIT_REPORT to a writable local JSON output path.
"""
import json
import os
from pathlib import Path

ICONS = ("health", "energy", "mana", "attack", "defense", "map")
CONTENT_DIRECTORY = "/Game/NARIS/UI/Icons"


def asset_path(name):
    if name not in ICONS:
        raise ValueError("Unrecognized original UI-017 icon")
    return f"{CONTENT_DIRECTORY}/{name}.{name}"


def audit_texture_assets(load_asset, texture_class):
    """Accept injectable read-only UE API methods for deterministic regression tests."""
    errors = []
    found = []
    for name in ICONS:
        path = asset_path(name)
        asset = load_asset(path)
        if asset is None:
            errors.append("Missing Texture2D asset: " + path)
            continue
        if not asset.is_a(texture_class):
            errors.append("Unexpected imported class: " + path)
            continue
        width = int(asset.blueprint_get_size_x())
        height = int(asset.blueprint_get_size_y())
        if (width, height) != (256, 256):
            errors.append(f"Wrong icon dimensions {name}: {width}x{height} (need 256x256)")
            continue
        found.append(path)
    return {
        "schema": "naris.ui017.texture-editor-audit.v1",
        "status": "IMPORT_ASSETS_PRESENT" if not errors else "BLOCKED",
        "icons": found,
        "errors": errors,
        "gameplay_rendered_in_pie": False,
        "full_unreal_build_tested": False,
        "release_approved": False,
    }


def run_unreal_asset_audit():
    import unreal  # Only when run inside actual Unreal Editor 5.7.
    output = os.environ.get("NARIS_UI017_AUDIT_REPORT")
    if not output:
        raise RuntimeError("Set NARIS_UI017_AUDIT_REPORT to an explicit output file")
    report_path = Path(output).resolve()
    if report_path.exists():
        raise RuntimeError("Refusing overwrite of a prior Unreal audit report")
    report = audit_texture_assets(unreal.EditorAssetLibrary.load_asset, unreal.Texture2D)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if report["status"] != "IMPORT_ASSETS_PRESENT":
        raise RuntimeError("Six authentic UI-017 icons not installed: " + "; ".join(report["errors"]))
    unreal.log("[UI-017] Read-only imported icon assets PASS; PIE and Windows cook STILL REQUIRED.")
    return report


if __name__ == "__main__":
    run_unreal_asset_audit()
