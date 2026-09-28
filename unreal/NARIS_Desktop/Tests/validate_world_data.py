from pathlib import Path
import csv, json, sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Content" / "Data"

def rows(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

zones = rows("DT_WorldZones.csv")
travel = rows("DT_FastTravelNodes.csv")
encounters = rows("DT_EncounterArchetypes.csv")
quests = rows("DT_Quests.csv")
objectives = rows("DT_QuestObjectives.csv")
biomes = rows("DT_Biomes.csv")

errors, warnings = [], []
zone_ids = {r["ZoneID"] for r in zones}
biome_ids = {r["BiomeID"] for r in biomes}
quest_ids = {r["QuestID"] for r in quests}

expected = [f"{i:02d}_" for i in range(9)]
for i, prefix in enumerate(expected):
    if i >= len(zones) or not zones[i]["ZoneID"].startswith(prefix):
        errors.append(f"Zone order mismatch at index {i}: expected {prefix}")
for r in zones:
    if r["BiomeID"] not in biome_ids:
        errors.append(f"Unknown biome {r['BiomeID']} in {r['ZoneID']}")

for r in travel:
    if r["ZoneID"] not in zone_ids:
        errors.append(f"FastTravel {r['NodeID']} references missing zone {r['ZoneID']}")

for r in encounters:
    if r["ZoneID"] not in zone_ids:
        errors.append(f"Encounter {r['Name']} references missing zone {r['ZoneID']}")

for r in objectives:
    if r["QuestID"] not in quest_ids:
        errors.append(f"Objective {r['ObjectiveID']} references missing quest {r['QuestID']}")
    if r["EventType"] == "ZoneDiscovered" and r["TargetID"] not in zone_ids:
        errors.append(f"Objective {r['ObjectiveID']} references missing zone {r['TargetID']}")

report = {
    "result": "PASS" if not errors else "FAIL",
    "zones": len(zones), "fast_travel_nodes": len(travel),
    "encounters": len(encounters), "quests": len(quests),
    "objectives": len(objectives), "errors": errors, "warnings": warnings,
}
(ROOT / "Tests" / "WORLD_DATA_VALIDATION.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(json.dumps(report, indent=2))
sys.exit(1 if errors else 0)
