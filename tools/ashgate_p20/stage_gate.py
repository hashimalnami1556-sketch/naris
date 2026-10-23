"""NARIS P20: verify four Ash Gate GLB layers before Unreal import."""
import hashlib
import json
import pathlib
import struct
import sys

LAYERS = ("SM_AshGate_Ground", "SM_AshGate_Architecture", "SM_AshGate_Foliage", "SM_AshGate_Props")

def verify_stage(asset_dir):
    root = pathlib.Path(asset_dir)
    errors = []
    try:
        layout = json.loads((root / "stage_layout.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"ok": False, "errors": [str(exc)]}
    for name in LAYERS:
        path = root / (name + ".glb")
        if not path.is_file():
            errors.append(name + ": missing")
            continue
        data = path.read_bytes()
        if len(data) < 20 or data[:4] != b"glTF":
            errors.append(name + ": invalid GLB signature")
        elif struct.unpack_from("<I", data, 8)[0] != len(data):
            errors.append(name + ": invalid GLB length")
        actual = hashlib.sha256(data).hexdigest()
        if actual != layout.get("sha256", {}).get(name):
            errors.append(name + ": SHA256 mismatch")
    if layout.get("player_spawn") != [-38, 0, 2]:
        errors.append("player spawn mismatch")
    if layout.get("boss_spawn") != [37, 0, 1.5]:
        errors.append("boss spawn mismatch")
    if layout.get("units") != "metres":
        errors.append("unit declaration mismatch")
    return {"ok": not errors, "errors": errors, "runtime_verified": False}

if __name__ == "__main__":
    result = verify_stage(sys.argv[1] if len(sys.argv) > 1 else "assets")
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["ok"] else 1)
