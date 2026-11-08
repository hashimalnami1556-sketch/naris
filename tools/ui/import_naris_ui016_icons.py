"""UI-016: import six original editable-SVG PNG exports as real UE Texture2D assets.

Run inside Unreal Editor 5.7 Python using:
  NARIS_UI016_ICON_ROOT=<extracted WORLD-015 package root>
  UnrealEditor-Cmd.exe NARIS_W04.uproject -ExecutePythonScript=<this file>

This script does not create/modify maps, widget Blueprints, save data or source
PNG/SVG files. It fails closed if any input hash changes or destination exists.
"""
import hashlib
import json
import os
from pathlib import Path

ICONS = ("health", "energy", "mana", "attack", "defense", "map")
DESTINATION = "/Game/NARIS/UI/Icons"
REQUIRED_APPROVED = {
    "UI_MainMenu_Approved.png",
    "UI_Character_Approved.png",
    "UI_Combat_Approved.png",
}


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_file(folder, filename, expected):
    if not filename or filename != Path(filename).name or "/" in filename or "\\" in filename:
        raise ValueError("Unsafe icon source filename")
    src = folder / filename
    if not src.is_file() or checksum(src) != expected:
        raise ValueError("Missing/modified approved source: " + str(src))
    return src


def validate_inputs(root):
    root = Path(root)
    path = root / "manifest.json"
    if not path.is_file():
        raise ValueError("WORLD-015 manifest.json missing")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    icons = manifest.get("ui_vector_icons", [])
    if len(icons) != 6 or {entry.get("name") for entry in icons} != set(ICONS):
        raise ValueError("UI-016 requires the exact six approved names")
    if len({entry.get("png_filename") for entry in icons}) != 6:
        raise ValueError("Duplicate icon PNG file")
    ui = manifest.get("original_ui_images", [])
    if len(ui) != 3 or {entry.get("filename") for entry in ui} != REQUIRED_APPROVED:
        raise ValueError("Three original approved screenshots absent")
    for item in ui:
        safe_file(root / "Approved_UI", item["filename"], item["sha256"])
    out = {}
    for item in icons:
        name = item["name"]
        if item["png_filename"] != name + ".png" or item["svg_filename"] != name + ".svg":
            raise ValueError("Unexpected SVG/PNG name mapping")
        # The canonical package locations are UI/IconsPng and UI/IconsSvg.
        safe_file(root / "UI" / "IconsSvg", item["svg_filename"], item["svg_sha256"])
        out[name] = safe_file(
            root / "UI" / "IconsPng", item["png_filename"], item["png_sha256"]
        )
    return out


def install():
    root = os.environ.get("NARIS_UI016_ICON_ROOT")
    if not root:
        raise RuntimeError("Set NARIS_UI016_ICON_ROOT to extracted WORLD-015 package directory")
    base = Path(root).resolve()
    files = validate_inputs(base)  # Verify all original UI/IconsPng inputs BEFORE touching UE.
    import unreal

    if unreal.EditorAssetLibrary.does_directory_exist(DESTINATION):
        raise RuntimeError(
            "Destination already exists. Inspect assets and preserve them: " + DESTINATION
        )
    for name in ICONS:
        if unreal.EditorAssetLibrary.does_asset_exist(
            DESTINATION + "/" + name
        ):
            raise RuntimeError("Refusing to replace existing icon: " + name)

    loaded = []
    for name in ICONS:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(files[name]))
        task.set_editor_property("destination_path", DESTINATION)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("replace_existing", False)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        expected_path = DESTINATION + "/" + name + "." + name
        paths = [str(p) for p in task.get_editor_property("imported_object_paths")]
        texture = unreal.EditorAssetLibrary.load_asset(expected_path)
        if expected_path not in paths or not texture or not texture.is_a(unreal.Texture2D):
            raise RuntimeError(
                "Texture2D import failed or name drifted: " + name
                + " imported: " + ", ".join(paths)
            )
        loaded.append(expected_path)
    if len(loaded) != 6:
        raise RuntimeError("Six native UMG Texture2D icons were not imported")
    output = {
        "schema": "naris.ui016.import.v1",
        "status": "TEXTURE2D_IMPORT_ONLY",
        "icon_assets": loaded,
        "original_screenshots_unchanged": True,
        "native_cpp_ui_bindings_also_required": True,
        "ue_play_in_editor_visual_test": "NOT_RUN",
        "windows_package_test": "NOT_RUN",
    }
    (base / "UI016_IMPORT_REPORT.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    unreal.log("[UI-016] Six Texture2D imported into native UMG icon path; visual QA required.")
    return output


if __name__ == "__main__":
    install()
