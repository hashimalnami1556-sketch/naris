"""Pure Stage29 rules. Source validation is never engine or PIE acceptance."""
import math


def vector3(value, positive=False):
    return (isinstance(value, list) and len(value) == 3
            and all(type(n) in (int, float) and math.isfinite(n)
                    and (not positive or n > 0) for n in value))


def validate_manifest(data, layout, policy):
    errors = []
    if data.get('schema') != 'naris.stage29.map-placements.v1':
        errors.append('Unsupported manifest schema')
    placements = data.get('placements')
    if not isinstance(placements, list):
        return ['placements must be an array']
    if len(placements) != 136:
        errors.append('Expected exactly 136 Stage29 placements')
    zones = {z['id']: z for z in layout['zones']}
    half_x = layout['bounds_m']['x'] * 50
    half_y = layout['bounds_m']['y'] * 50
    seen = set()
    for i, p in enumerate(placements):
        if not isinstance(p, dict):
            errors.append(f'Row {i}: expected object'); continue
        name = p.get('id')
        if not isinstance(name, str) or not name or name in seen:
            errors.append(f'Row {i}: missing/duplicate ID')
        if isinstance(name, str): seen.add(name)
        if p.get('zone') not in zones: errors.append(f'{name}: unknown zone')
        key = p.get('asset_key')
        if not isinstance(key, str) or key not in policy:
            errors.append(f'{name}: missing role/collision policy')
        elif policy[key].get('collision') not in ('solid', 'decoration'):
            errors.append(f'{name}: unsupported collision role')
        t = p.get('transform', {})
        if not isinstance(t, dict): t = {}
        for field in ('location_cm', 'rotation_deg', 'scale'):
            if not vector3(t.get(field), positive=field == 'scale'):
                errors.append(f'{name}: invalid {field}')
        if vector3(t.get('location_cm')):
            x, y, _ = t['location_cm']
            if not (-half_x <= x <= half_x and -half_y <= y <= half_y):
                errors.append(f'{name}: outside centered canonical XY bounds')
            if p.get('zone') in zones:
                zone = zones[p['zone']]
                if any(abs(t['location_cm'][i]/100-zone['center'][i]) > zone['size'][i]/2 for i in range(2)):
                    errors.append(f'{name}: outside its declared canonical zone')
    return errors


def resolve_asset(key, candidates, explicit=None):
    """Exact basename preferred; an explicit object path resolves importer suffixes."""
    if explicit:
        return explicit if explicit in candidates else None
    matches = [p for p in candidates if p.rsplit('/', 1)[-1].split('.')[0].lower() == key.lower()]
    return matches[0] if len(matches) == 1 else None


def decide_g1(report):
    """Engine authoring cannot satisfy the required runtime/visual review fields."""
    errors = list(report.get('errors', []))
    if report.get('engine_executed') is not True: errors.append('Unreal execution required')
    if report.get('mode') != 'apply': errors.append('Actual measured authoring run required')
    rows = report.get('elements', [])
    ids = [r.get('id') for r in rows]
    if len(rows) != 136 or len(set(ids)) != 136 or not all(ids):
        errors.append('136 unique measured elements required')
    if report.get('map_saved') is not True: errors.append('Saved engine map required')
    for row in rows:
        if row.get('status') != 'placed': errors.append(f"{row.get('id')}: not placed")
        for check in ('bounds_ok', 'materials_assigned', 'collision_ok', 'ground_ok', 'scale_ok', 'rotation_ok'):
            if row.get(check) is not True: errors.append(f"{row.get('id')}: {check} unproven")
    review = report.get('runtime_review', {})
    if review.get('run_id') != report.get('run_id') or not report.get('run_id'):
        errors.append('Runtime evidence must match the authoring run')
    if set(review.get('visible_element_ids', [])) != set(ids):
        errors.append('PIE evidence must cover every measured element ID')
    for field in ('pie_visibility', 'visual_materials', 'streaming_culling', 'ground_traversal', 'material_budget'):
        if review.get(field) != 'PASS': errors.append(f'{field}: not verified in engine')
    return {'decision': 'G1 FAIL' if errors and report.get('engine_executed') and report.get('mode') == 'apply' else 'G1 BLOCKED',
            'blocking_issues': errors} if errors else {'decision': 'G1 PASS', 'blocking_issues': []}
