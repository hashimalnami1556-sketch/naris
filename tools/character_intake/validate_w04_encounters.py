"""Offline validator for W04 encounter data. Not a UE runtime test."""
import json
import pathlib
import sys

def validate(data):
    issues = []
    zones = data.get("zones", [])
    if len(zones) != 3:
        issues.append("expected exactly 3 launch zones")
    ids = [z.get("id") for z in zones]
    if len(set(ids)) != len(ids):
        issues.append("duplicate zone ids")
    for z in zones:
        name = z.get("id", "<missing>")
        if not z.get("checkpoint") or not z.get("loot_table"):
            issues.append(f"{name}: missing checkpoint/loot")
        if not z.get("enemy_spawns"):
            issues.append(f"{name}: no enemies")
        for e in z.get("enemy_spawns", []):
            if not e.get("id") or e.get("count", 0) <= 0:
                issues.append(f"{name}: invalid enemy spawn")
        boss = z.get("boss", {})
        if boss.get("hp", 0) <= 0 or boss.get("poise", 0) <= 0:
            issues.append(f"{name}: invalid boss stats")
        phases = boss.get("phases", [])
        if len(phases) < 2 or phases[0].get("at_hp_ratio") != 1:
            issues.append(f"{name}: expected two boss phases starting at full HP")
        if any(not (0 < p.get("at_hp_ratio", 0) <= 1) or not p.get("attack_set") for p in phases):
            issues.append(f"{name}: invalid boss phase")
    if data.get("integration", {}).get("ue_editor_executed") is not False:
        issues.append("unverified engine execution must remain false")
    return issues

if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2] / "data/gameplay/NARIS_W04_ENCOUNTERS_V1.json"
    issues = validate(json.loads(path.read_text(encoding="utf-8")))
    print("PASS: 3-zone encounter data" if not issues else "\n".join(issues))
    sys.exit(bool(issues))
