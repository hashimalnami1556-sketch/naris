"""NARIS build preflight: checks the source GLBs before attempting Blender rigging.
Standalone Python 3.10+, no external dependencies. Does not modify assets.
"""
import argparse
import json
import struct
from pathlib import Path

def inspect_glb(path):
    path = Path(path)
    with path.open("rb") as stream:
        header = stream.read(20)
        if len(header) != 20:
            raise ValueError("Truncated GLB header")
        magic, version, size, length, kind = struct.unpack("<4sIII4s", header)
        if magic != b"glTF" or version != 2 or size != path.stat().st_size or kind != b"JSON":
            raise ValueError("Invalid GLB header")
        if length > size - 20 or length > 64 * 1024 * 1024:
            raise ValueError("Invalid JSON length")
        doc = json.loads(stream.read(length).decode("utf-8").rstrip(" " + chr(0)))
    return {"meshes": len(doc.get("meshes", [])), "skins": len(doc.get("skins", [])), "animations": len(doc.get("animations", []))}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Directory containing Character 1.glb and Character 3.glb")
    args = parser.parse_args()
    source = Path(args.source)
    results = {}
    failed = False
    for name in ("Character 1.glb", "Character 3.glb"):
        try:
            results[name] = inspect_glb(source / name)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            results[name] = {"error": str(exc)}
            failed = True
    print(json.dumps(results, indent=2))
    raise SystemExit(1 if failed else 0)

if __name__ == "__main__":
    main()
