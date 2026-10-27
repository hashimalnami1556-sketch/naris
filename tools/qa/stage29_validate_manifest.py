from pathlib import Path
import json
m=json.loads((Path(__file__).resolve().parents[3]/"stage29_population_manifest.json").read_text(encoding="utf-8"))
assert m["schema"]=="naris.stage29.population.v1"
assert len(m["zones"])==6 and len(m["placements"])==136 and len(m["assets"])==23
assert len({p["id"] for p in m["placements"]})==136
assert all("original_location_cm" in p["transform"] for p in m["placements"])
print("Stage29 structural manifest pass — NOT Unreal runtime QA")
