"""Translate received Stage29 zone clusters to canonical centers; no scale/clamp."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'unreal/NARIS_W04/Content/NARIS/W04/Production/Stage29'


def remap(data, layout):
    result = copy.deepcopy(data)
    shifts = {}
    for zone in layout['zones']:
        rows = [p for p in data['placements'] if p['zone'] == zone['id']]
        if not rows: raise ValueError('Missing zone: ' + zone['id'])
        centroid = [sum(p['transform']['location_cm'][i] for p in rows)/len(rows) for i in range(2)]
        shifts[zone['id']] = [zone['center'][i]*100-centroid[i] for i in range(2)]
    for row in result['placements']:
        old = row['transform']['location_cm']
        row['transform']['location_cm'] = [old[i]+shifts[row['zone']][i] for i in range(2)] + [old[2]]
    result['coordinate_correction'] = 'Review candidate: translate each received zone XY centroid to canonical LEVEL_LAYOUT center; no rotation, scale, clamp or within-zone distance change. Z requires engine ground trace.'
    result['zone_translation_cm'] = shifts
    result['status'] = 'review_candidate_not_engine_verified'
    return result


def main():
    path = FOLDER/'placements_received.json'
    source = json.loads(path.read_text())
    layout = json.loads((ROOT/'NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json').read_text())
    result = remap(source, layout)
    result['received_manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (FOLDER/'placements_corrected.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__': main()
