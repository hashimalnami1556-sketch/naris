"""Pure structural map checks; these do not certify gameplay or performance."""
from collections import Counter


def evaluate_snapshot(requirements: dict, actors: list[dict]) -> dict:
    required_labels = set(requirements.get('required_actor_labels', []))
    required_labels.update(z['label'] for z in requirements.get('zones', []) if z.get('label'))
    required_classes = set(requirements.get('required_actor_classes', []))
    counts = Counter(a['label'] for a in actors)
    labels = set(counts)
    classes = {name for actor in actors for name in actor.get('class_names', [])}
    prefixes = tuple(requirements.get('forbidden_label_prefixes', [])) + ('REVIEW_', 'PROTOTYPE_REFERENCE')
    mismatches = []
    expected = requirements.get('required_actor_label_classes', {})
    for actor in actors:
        name = expected.get(actor['label'])
        if name and name not in actor.get('class_names', []):
            mismatches.append({'label': actor['label'], 'expected': name})
    prototype_meshes = [
        {'label': actor['label'], 'mesh': mesh}
        for actor in actors for mesh in actor.get('static_mesh_paths', [])
        if mesh.startswith('/Engine/BasicShapes/')
    ]
    result = {
        'required_labels': sorted(required_labels),
        'missing_labels': sorted(required_labels - labels),
        'required_actor_classes': sorted(required_classes),
        'missing_actor_classes': sorted(required_classes - classes),
        'forbidden_labels_found': sorted(set(requirements.get('forbidden_actor_labels', [])) & labels),
        'forbidden_prefix_labels_found': sorted(label for label in labels if label.startswith(prefixes)),
        'duplicate_required_labels': sorted(label for label in required_labels if counts[label] > 1),
        'class_mismatches': mismatches,
        'prototype_meshes': prototype_meshes,
        'errors': [],
    }
    if not required_labels or not required_classes:
        result['errors'].append('Empty production map contract')
    for field in ('missing_labels', 'missing_actor_classes', 'forbidden_labels_found',
                  'forbidden_prefix_labels_found', 'duplicate_required_labels', 'class_mismatches', 'prototype_meshes'):
        if result[field]:
            result['errors'].append('Production map gate failed: ' + field)
    return result
