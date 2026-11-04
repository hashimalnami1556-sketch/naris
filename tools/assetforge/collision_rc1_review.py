"""Non-destructive GLB collision review ONLY (no Unreal claims).

Usage: python tools/assetforge/collision_rc1_review.py <source_glb> <output_candidate_glb>
Requires trimesh, numpy. Result is never production collision.
"""
import argparse
import hashlib
import json
from pathlib import Path


def inspect_and_generate(source: Path, dest: Path):
    import trimesh
    if source.suffix.lower() != ".glb":
        raise ValueError("GLB source required; source file not modified")
    if source.resolve() == dest.resolve():
        raise ValueError("Refusing to overwrite original mesh")
    scene = trimesh.load(str(source), force="scene")
    geom = scene.to_geometry()
    if not isinstance(geom, trimesh.Trimesh) or len(geom.faces) == 0:
        raise ValueError("Expected non-empty original triangle geometry")
    dest.parent.mkdir(parents=True, exist_ok=True)
    hull = geom.convex_hull
    hull.export(str(dest))
    return {
        "original": source.name,
        "original_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "original_triangles": len(geom.faces),
        "candidate_triangles": len(hull.faces),
        "status": "MANUAL_REVIEW_REQUIRED",
        "unreal_tested": False,
        "units_verified": False,
        "warning": "Single hull closes holes, doors and archways; never enable on traversable architecture without splitting",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_and_generate(args.source, args.candidate), indent=2))
