"""WORLD-013: strict offline integrity gate for the self-contained Unreal world handoff.

This checks actual file bytes, not whether Unreal or its map has run. Return 2 on failure.
Usage: python tools/ci/verify_world013_package.py /path/to/NARIS_WORLD_013_REAL
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ORIGINAL_ASSETS = {
    "Character 1.glb", "Character 3.glb",
    "Character1_NARIS_Rigged_Prototype.glb",
    "Environmental 1.glb", "City 1.glb",
}
ORIGINAL_UI = {
    "UI_MainMenu_Approved.png",
    "UI_Character_Approved.png",
    "UI_Combat_Approved.png",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(root: Path) -> dict:
    root = Path(root).resolve()
    errors = []
    manifest_file = root / "manifest.json"
    if not manifest_file.is_file():
        return {"status": "BLOCKED", "errors": ["manifest.json missing"]}
    payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    if payload.get("schema") != "naris.world013.1":
        errors.append("unsupported schema")
    assets = payload.get("source_assets", [])
    ui = payload.get("original_ui_images", [])
    tiles = payload.get("terrain_tiles", [])
    if {x.get("filename") for x in assets} != ORIGINAL_ASSETS:
        errors.append("original GLB list does not match")
    if {x.get("filename") for x in ui} != ORIGINAL_UI:
        errors.append("approved UI PNG list does not match")
    if len(tiles) != 64 or len({x.get("filename") for x in tiles}) != 64:
        errors.append("missing or duplicated terrain tiles")
    if sum(int(x.get("triangle_count", 0)) for x in tiles) != 508032:
        errors.append("wrong source-derived terrain face count")
    if payload.get("scatter_count") != 2990:
        errors.append("original scatter count changed")
    if payload.get("default_map_modified") is not False:
        errors.append("GameDefaultMap must remain unchanged")
    for directory, values in (
        ("Source", assets), ("Approved_UI", ui), ("Terrain/Chunks", tiles)
    ):
        for item in values:
            name = item.get("filename", "")
            if not name or Path(name).name != name or "/" in name or "\\" in name:
                errors.append("unsafe package filename: " + name)
                continue
            p = root / directory / name
            if not p.is_file():
                errors.append("missing " + str(p))
            elif sha256(p) != item.get("sha256"):
                errors.append("digest mismatch " + name)
    raw = root / "Heightmaps/NARIS_2km_1009.r16"
    if not raw.is_file() or raw.stat().st_size != 1009 * 1009 * 2:
        errors.append("R16 absent or wrong byte count")
    elif sha256(raw) != payload.get("source_heightmap_sha256"):
        errors.append("R16 changed")
    return {
        "status": "OFFLINE_FILES_VALID" if not errors else "BLOCKED",
        "errors": errors,
        "original_GLBS": len(assets),
        "approved_UI_PNGs": len(ui),
        "terrain_chunks": len(tiles),
        "unreal_run": False,
        "map_saved": False,
        "umg_integrated": False,
        "release_approved": False,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/ci/verify_world013_package.py <extracted package root>")
    result = verify(Path(sys.argv[1]))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "OFFLINE_FILES_VALID" else 2)
