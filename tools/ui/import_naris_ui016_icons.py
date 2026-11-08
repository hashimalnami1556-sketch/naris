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


# Source-of-truth digests live in the repository, independent of the
# packaged manifest. Replacing both an image and its package manifest is NOT
# sufficient to pass this importer.
PINNED_UI_SHA256 = {
    "UI_MainMenu_Approved.png": "8d216d0a12d39e76a127ac00e20a121b0ca4833be873b00cddf170708e48882f",
    "UI_Character_Approved.png": "ff2e0f04146edeb7c9ce75e624e9c5738d0e576b6b4c86a45e6e008a0b9e9f71",
    "UI_Combat_Approved.png": "19734e1aa77206378c915e39d2505d941cc6de4f962b5bd270636ba2ddaa25d6",
}
PINNED_ICON_PNG_SHA256 = {
    "health": "3cae48098ea8307fb852e6c486ebec1578e465d961d26a6ac9a525735239bb2b",
    "energy": "c2a4797a5131cf1727927cc16aba460e94f436284a28e10a37ea3685cabb6013",
    "mana": "51673d1c8196531254f18cab515fcafa00124011f09c7dcbd194e75aa5cbc479",
    "attack": "a28c933ec06f801e007e87f0c5c3576dc5ef8e3ca1fcdee358258bc6a4be85e5",
    "defense": "1182abcf9ed770f7a44a3af503c0f6c09cd8256ac3354cf1157804f0bd96b222",
    "map": "c4e90757fc2f07019e928099bcf0775d264ed593d3e1858c89931f88aa46e2a0",
}

PINNED_ICON_SVG_SHA256 = {
    "health": "8a6bc5a0b4d6b6d685659c3e8de66db707ebe193480829db6fb4cb1d1120c67a",
    "energy": "26a13bd67cdc2a3fc1ba9b3449eaab924ecf6d18a0c10852b720b24c48fbf2ee",
    "mana": "73ad9eb1f4d59e903ae9459e50279e31c8e67ea0f23e940032304098be35dd66",
    "attack": "2ffc06544fa04c80bf255d185130f042bd1d7b6d69a245f89b0bde6fa82bfcd6",
    "defense": "094b724b6e6acfb5480b1b6ef020adf5379a32cd59255290585e0a57c215cdd7",
    "map": "3e61eeb1b1909389662a5b0b66bd716531119b0833b6731571cbf42ff849bd9a",
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
        if item["sha256"] != PINNED_UI_SHA256.get(item["filename"]):
            raise ValueError("Original approved image digest differs from locked source")
        safe_file(root / "Approved_UI", item["filename"], item["sha256"])
    out = {}
    for item in icons:
        name = item["name"]
        if item["png_filename"] != name + ".png" or item["svg_filename"] != name + ".svg":
            raise ValueError("Unexpected SVG/PNG name mapping")
        if item["png_sha256"] != PINNED_ICON_PNG_SHA256[name]:
            raise ValueError("Icon PNG digest differs from locked source: " + name)
        if item["svg_sha256"] != PINNED_ICON_SVG_SHA256[name]:
            raise ValueError("Icon SVG digest differs from locked vector source: " + name)
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
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        root = os.environ.get("NARIS_UI016_ICON_ROOT")
        if not root:
            raise SystemExit("Set NARIS_UI016_ICON_ROOT before --check")
        validated = validate_inputs(Path(root))
        print("[UI-016] Offline byte-for-byte approved originals + six PNG/SVG assets PASS:", sorted(validated))
    else:
        install()
