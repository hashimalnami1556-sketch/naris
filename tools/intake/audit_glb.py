"""Validate embedded GLB geometry before editor intake; not visual/engine approval."""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

FORMATS = {5120: 'b', 5121: 'B', 5122: 'h', 5123: 'H', 5125: 'I', 5126: 'f'}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def load_glb(path):
    raw = Path(path).read_bytes()
    if len(raw) < 20 or struct.unpack_from('<4sII', raw) != (b'glTF', 2, len(raw)):
        raise ValueError('Invalid GLB header/length')
    chunks = []; offset = 12
    while offset < len(raw):
        size, kind = struct.unpack_from('<II', raw, offset); offset += 8
        if size % 4 or offset + size > len(raw):
            raise ValueError('Invalid GLB chunk boundary')
        chunks.append((kind, raw[offset:offset + size])); offset += size
    if not chunks or chunks[0][0] != 0x4E4F534A:
        raise ValueError('Missing JSON chunk')
    doc = json.loads(chunks[0][1])
    binary = next((b for k, b in chunks if k == 0x004E4942), b'')
    if any('uri' in b for b in doc.get('buffers', [])):
        raise ValueError('External buffers are not supported by this intake')
    if any('uri' in im for im in doc.get('images', [])):
        raise ValueError('External textures must be embedded for this intake')
    return raw, doc, binary


def accessor(doc, binary, index):
    a = doc['accessors'][index]
    if 'sparse' in a:
        raise ValueError('Sparse accessor requires a dedicated validator')
    v = doc['bufferViews'][a['bufferView']]
    if v.get('buffer', 0) != 0:
        raise ValueError('Only the embedded buffer is supported')
    fmt = '<' + FORMATS[a['componentType']] * WIDTHS[a['type']]
    size = struct.calcsize(fmt); stride = v.get('byteStride', size)
    start = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    end = start + max(0, a['count'] - 1) * stride + (size if a['count'] else 0)
    if stride < size or end > v.get('byteOffset', 0) + v['byteLength'] or end > len(binary):
        raise ValueError('Accessor exceeds its buffer view')
    values = [struct.unpack_from(fmt, binary, start + i * stride) for i in range(a['count'])]
    if a.get('normalized') and a['componentType'] != 5126:
        maxima = {5120: 127, 5121: 255, 5122: 32767, 5123: 65535, 5125: 4294967295}
        values = [tuple(max(-1, x / maxima[a['componentType']]) for x in row) for row in values]
    return values


def audit(path):
    raw, doc, binary = load_glb(path)
    for i in range(len(doc.get('accessors', []))):
        values = accessor(doc, binary, i)
        if any(not math.isfinite(x) for row in values for x in row):
            raise ValueError('Non-finite accessor')
    primitives = []; warnings = []
    for mesh in doc.get('meshes', []):
        for p in mesh.get('primitives', []):
            if p.get('mode', 4) != 4:
                raise ValueError('Only triangle primitives supported')
            attributes = p['attributes']; positions = accessor(doc, binary, attributes['POSITION'])
            indices = [row[0] for row in accessor(doc, binary, p['indices'])] if 'indices' in p else list(range(len(positions)))
            if len(indices) % 3 or any(i < 0 or i >= len(positions) for i in indices):
                raise ValueError('Invalid triangle indices')
            bad_weights = 0
            if 'WEIGHTS_0' in attributes:
                weights = accessor(doc, binary, attributes['WEIGHTS_0'])
                if len(weights) != len(positions):
                    raise ValueError('Weight/vertex count mismatch')
                bad_weights = sum(any(x < 0 for x in row) or abs(sum(row) - 1) > 0.001 for row in weights)
            if bad_weights:
                raise ValueError(f'{bad_weights} invalid vertex weights')
            for key in attributes:
                if len(accessor(doc, binary, attributes[key])) != len(positions):
                    raise ValueError(f'{key} count mismatch')
            primitives.append({'vertices': len(positions), 'triangles': len(indices)//3,
                'bounds_min': [min(v[k] for v in positions) for k in range(3)],
                'bounds_max': [max(v[k] for v in positions) for k in range(3)],
                'attributes': sorted(attributes)})
    for node in doc.get('nodes', []):
        if 'skin' in node and 'mesh' in node:
            skin = doc['skins'][node['skin']]
            for p in doc['meshes'][node['mesh']]['primitives']:
                joints = accessor(doc, binary, p['attributes']['JOINTS_0'])
                if any(j >= len(skin['joints']) for row in joints for j in row):
                    raise ValueError('Joint index outside skin')
    for skin in doc.get('skins', []):
        if any(j >= len(doc.get('nodes', [])) for j in skin['joints']):
            raise ValueError('Skin references missing node')
    if not doc.get('skins'): warnings.append('No skeleton; display mesh only')
    animations = [{'name': a.get('name', ''), 'channels': len(a.get('channels', [])),
        'target_paths': sorted({c['target']['path'] for c in a.get('channels', [])})} for a in doc.get('animations', [])]
    if len(animations) < 2: warnings.append('No verified locomotion/combat animation set')
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'geometry_validation': 'pass',
        'primitives': primitives, 'triangles': sum(p['triangles'] for p in primitives),
        'joint_counts': [len(s['joints']) for s in doc.get('skins', [])], 'animations': animations,
        'materials': len(doc.get('materials', [])), 'embedded_images': len(doc.get('images', [])),
        'warnings': warnings, 'engine_import': 'not_run', 'production_approved': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('files', nargs='+'); args = parser.parse_args()
    print(json.dumps({str(p): audit(p) for p in args.files}, indent=2))
