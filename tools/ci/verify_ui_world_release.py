"""Read-only W04 visual and world release preflight. Missing assets BLOCK release."""
import argparse
import hashlib
import json
import re
from pathlib import Path

FILES = {"UI_MainMenu_Approved.png", "UI_Character_Approved.png", "UI_Combat_Approved.png"}

def check(root, references=None):
    root = Path(root)
    project = root / "unreal/NARIS_W04"
    source = project / "Source/NARIS_W04/Private"
    menu = source / "NarisSystemMenuWidget.cpp"
    hud = source / "NarisHUD.cpp"
    world = project / "Content/NARIS/W04/Maps/W04_AshenForest.umap"
    ini = project / "Config/DefaultEngine.ini"
    manifest = root / "docs/ui/references/UI-002/manifest.json"
    checks = {
        "uproject": (project / "NARIS_W04.uproject").is_file(),
        "production_world": world.is_file() and world.stat().st_size > 1024,
        "approved_ui_manifest": False,
        "approved_ui_png_sha256": False,
        "production_map_default": False,
        "right_menu": False,
        "live_inventory": False,
        "boss_top": False,
        "live_boss_hp": False,
    }
    if menu.is_file() and hud.is_file():
        m = menu.read_text(encoding="utf-8")
        h = hud.read_text(encoding="utf-8")
        checks["right_menu"] = "FAnchors(0.71f, 0.27f, 0.95f, 0.83f)" in m
        checks["live_inventory"] = "State.EquippedItems[Index]" in m and "State.InventoryItems[Index]" in m
        checks["boss_top"] = "const float Y = Safe + 12.f * Scale;" in h
        checks["live_boss_hp"] = "Boss->GetCurrentHealth()" in h and "Boss->GetConfiguredMaxHealth()" in h
    if ini.is_file():
        match = re.search(r"(?m)^GameDefaultMap\s*=\s*(\S+)", ini.read_text(encoding="utf-8"))
        checks["production_map_default"] = bool(match and match.group(1) == "/Game/NARIS/W04/Maps/W04_AshenForest")
    if manifest.is_file():
        try:
            entries = json.loads(manifest.read_text(encoding="utf-8"))["images"]
            checks["approved_ui_manifest"] = len(entries) == 3 and {x["file"] for x in entries} == FILES
            if references and checks["approved_ui_manifest"]:
                refs = Path(references)
                checks["approved_ui_png_sha256"] = all(
                    (refs / x["file"]).is_file() and
                    hashlib.sha256((refs / x["file"]).read_bytes()).hexdigest() == x["sha256"]
                    for x in entries)
        except (ValueError, TypeError, KeyError, OSError):
            pass
    return {"status": "PASS_OFFLINE_PREFLIGHT" if all(checks.values()) else "BLOCKED",
            "checks": checks, "unreal_runtime_verified": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--references", type=Path)
    args = parser.parse_args()
    report = check(args.repo_root, args.references)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "PASS_OFFLINE_PREFLIGHT" else 2)
