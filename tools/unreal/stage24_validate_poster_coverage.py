#!/usr/bin/env python3
"""Validate the approved poster roster without claiming engine validation."""
from __future__ import annotations
import json
from pathlib import Path

POSTER_ROSTER = (
    "The_Hero", "Veil_Mother", "Bone_Hound", "Mist_Guardian",
    "Demon_Warrior", "Aether_Serpent", "Dragon", "Shadow_Assassin",
    "Forest_Witch", "Frost_Giant", "Stone_Golem", "Plague_Beast",
    "Sand_Wraith", "Crimson_Hunter", "Soul_Reaper", "Ember_Knight",
    "Lumen_Priest", "Naris_Archmage", "Void_Knight",
    "Corrupted_Druid", "Siren", "Undying_King", "Rift_Spawn",
    "Naris_Beastlord", "The_Exiled_Queen",
)
# The Stage23 registry file is included in the downloadable Stage24 pack,
# not yet committed as a binary model delivery.
def audit_registry(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    rows = manifest["coverage"]
    names = {row["poster_character"] for row in rows}
    assert set(POSTER_ROSTER) == names, "Poster roster mismatch"
    assert len(rows) == 150, "Expected 25 x 6 motion slots"
    assert all(len([row for row in rows if row["poster_character"] == name]) == 6 for name in POSTER_ROSTER)
    models = manifest["models"]
    assert len(models) == 10
    unresolved = sum(row["implementation"] != "GLB_procedural_study" for row in rows)
    assert unresolved == len(manifest["unresolved"])
    return {"characters": len(names), "motion_slots": len(rows), "prototype_models": len(models),
            "not_mapped_to_study": unresolved, "unreal_verified": False}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path, help="Stage24 registry/poster_motion_registry.json")
    args = parser.parse_args()
    print(json.dumps(audit_registry(args.registry), indent=2))
