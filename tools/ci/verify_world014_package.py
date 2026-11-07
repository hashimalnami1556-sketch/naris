"""Fail-closed WORLD-014 package gate: source hashes + R16-ground landmarks.
Run: python tools/ci/verify_world014_package.py <unpacked_world014_root>
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assetforge"))
sys.path.insert(0, str(ROOT / "ci"))
from world014_ground_alignment import landmark_ground_m
from verify_world013_package import verify as verify_old


def verify_world014(package_root):
    package = Path(package_root)
    original = verify_old(package)
    errors = list(original.get("errors", []))
    if original.get("status") != "OFFLINE_FILES_VALID":
        errors.append("WORLD-013 base source integrity failed")
    manifest_path = package / "manifest.json"
    if manifest_path.is_file():
        try:
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            landmarks = m.get("environment_landmarks", [])
            if len(landmarks) != 2:
                errors.append("Expected exactly two original City/Environment review landmarks")
            r16 = package / "Heightmaps/NARIS_2km_1009.r16"
            for item in landmarks:
                x, y, z = item["location_m_xyz"]
                ground = landmark_ground_m(r16, x, y, m.get("source_heightmap_sha256"))
                if abs(z - ground) > .02:
                    errors.append("Landmark source-ground mismatch: " + item.get("zone", "?"))
        except (ValueError, TypeError, KeyError, OSError) as ex:
            errors.append("Invalid landmark R16 data: " + str(ex))
    else:
        errors.append("Missing manifest.json")
    script_path = package / "Tools/ue57_build_world.py"
    if not script_path.is_file():
        errors.append("Missing Unreal 5.7 world authoring script")
    else:
        source = script_path.read_text(encoding="utf-8")
        if "W04_AshenForest_Work014" not in source or "z*100" not in source:
            errors.append("World014 editor script missing correct map path or Z placement")
        if "does_asset_exist(LEVEL_PATH)" not in source or "is_partitioned_world=True" not in source:
            errors.append("World014 editor safety checks missing")
    return {
        "status": "OFFLINE_FILES_VALID" if not errors else "BLOCKED",
        "errors": errors,
        "unreal_57_executed": False,
        "windows_exe_built": False,
        "engine_qa_passed": False,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: verify_world014_package.py <unpacked package root>")
    result = verify_world014(Path(sys.argv[1]))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "OFFLINE_FILES_VALID" else 2)
