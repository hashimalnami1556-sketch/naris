"""Validate the NARIS Rig Expansion ZIP before importing binaries into Unreal.

Usage: python tools/character_intake/check_rig_bundle.py NARIS_RIG_EXPANSION_20261012_FULL.zip
Offline checks only. This does NOT validate skinned deformation or gameplay.
"""
import argparse
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path


def glb_metadata(archive, path):
    with archive.open(path) as reader:
        header = reader.read(20)
        if len(header) != 20:
            raise ValueError("Truncated GLB")
        magic, version, total, size, chunk = struct.unpack("<4sIIII", header)
        if magic != b"glTF" or version != 2 or chunk != 0x4E4F534A or size % 4:
            raise ValueError("Invalid glTF 2.0 JSON header")
        document = json.loads(reader.read(size))
    if archive.getinfo(path).file_size != total:
        raise ValueError("GLB declared size does not match actual size")
    return document


def main(pack):
    errors = []
    prefix = "NARIS_RIG_EXPANSION_20261012/"
    with zipfile.ZipFile(pack) as archive:
        manifest = json.loads(archive.read(prefix + "bundle_files.sha256.json"))
        for item in manifest["files"]:
            path = prefix + item["file"]
            try:
                checksum = hashlib.sha256()
                with archive.open(path) as reader:
                    while block := reader.read(1024 * 1024):
                        checksum.update(block)
                if checksum.hexdigest() != item["sha256"]:
                    raise ValueError("SHA256 mismatch")
                if archive.getinfo(path).file_size != item["bytes"]:
                    raise ValueError("Size mismatch")
            except Exception as exc:
                errors.append({"file": path, "error": str(exc)})

        rigged = json.loads(archive.read(prefix + "glb/asset_manifest.json"))
        static = json.loads(archive.read(prefix + "worldkit/worldkit_manifest.json"))
        if len(rigged) != 6 or len(static) != 4:
            errors.append({"error": "Expected six rigged and four static assets"})

        for entry in rigged:
            path = prefix + "glb/" + entry["path"]
            try:
                document = glb_metadata(archive, path)
                skins = document.get("skins", [])
                if len(skins) != 1 or len(skins[0]["joints"]) != entry["bones"]:
                    raise ValueError("Incorrect rig or bone count")
                if len(document.get("animations", [])) != len(entry["animations"]):
                    raise ValueError("Incorrect embedded clip count")
                if not any("mesh" in n and "skin" in n for n in document.get("nodes", [])):
                    raise ValueError("Mesh not attached to skin")
            except Exception as exc:
                errors.append({"file": path, "error": str(exc)})

        for entry in static:
            path = prefix + "worldkit/" + entry["file"]
            try:
                document = glb_metadata(archive, path)
                if document.get("skins") or not document.get("meshes"):
                    raise ValueError("Invalid static world asset")
            except Exception as exc:
                errors.append({"file": path, "error": str(exc)})

    print(json.dumps({"status": "PASS" if not errors else "FAIL",
                      "rigged_variants": len(rigged), "world_variants": len(static),
                      "sha256_files_checked": len(manifest["files"]),
                      "Unreal_playtest_completed": False,
                      "errors": errors}, indent=2, ensure_ascii=False))
    return int(bool(errors))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    sys.exit(main(args.archive))
