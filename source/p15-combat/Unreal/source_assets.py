"""Limited embedded-GLB intake and bind-pose checks; not a full glTF conformance validator."""
import hashlib
import json
import math
from pathlib import Path
import struct

IDENTITY = [[float(i == j) for j in range(4)] for i in range(4)]


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def inverse(a):
    rows = [list(row) + list(IDENTITY[i]) for i, row in enumerate(a)]
    for col in range(4):
        pivot = max(range(col, 4), key=lambda i: abs(rows[i][col]))
        if abs(rows[pivot][col]) < 1e-12:
            raise ValueError('Singular bind transform')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [v / divisor for v in rows[col]]
        for i in range(4):
            if i != col:
                factor = rows[i][col]
                rows[i] = [v - factor * w for v, w in zip(rows[i], rows[col])]
    return [row[4:] for row in rows]


def matrix(values):
    return [[values[col * 4 + row] for col in range(4)] for row in range(4)]


def flatten(a):
    return [a[row][col] for col in range(4) for row in range(4)]


def local_matrix(node):
    if 'matrix' in node:
        if len(node['matrix']) != 16:
            raise ValueError('Node matrix must have 16 values')
        return matrix(node['matrix'])
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    if abs(x*x + y*y + z*z + w*w - 1) > 1e-4:
        raise ValueError('Node quaternion is not normalized')
    scale = node.get('scale', [1, 1, 1])
    translation = node.get('translation', [0, 0, 0])
    rotation = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    return [[rotation[i][j] * scale[j] for j in range(3)] + [translation[i]] for i in range(3)] + [[0, 0, 0, 1]]


class GLB:
    def __init__(self, payload):
        self.payload = payload
        if len(payload) < 20:
            raise ValueError('Truncated GLB')
        magic, version, length = struct.unpack_from('<4sII', payload)
        if magic != b'glTF' or version != 2 or length != len(payload):
            raise ValueError('GLB magic, version or declared length mismatch')
        chunks = []
        offset = 12
        while offset < len(payload):
            if offset + 8 > len(payload):
                raise ValueError('Truncated GLB chunk header')
            count, kind = struct.unpack_from('<II', payload, offset)
            offset += 8
            if count % 4 or offset + count > len(payload):
                raise ValueError('GLB chunk length/alignment mismatch')
            chunks.append((kind, payload[offset:offset+count]))
            offset += count
        if not chunks or chunks[0][0] != 0x4E4F534A:
            raise ValueError('First GLB chunk must be JSON')
        if len(chunks) != 2 or chunks[1][0] != 0x004E4942:
            raise ValueError('This intake supports one embedded JSON/BIN pair only')
        self.doc = json.loads(chunks[0][1].decode('utf-8'), parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
        if self.doc.get('asset', {}).get('version') != '2.0':
            raise ValueError('Expected glTF asset version 2.0')
        self.binary = bytearray(chunks[1][1])
        buffers = self.doc.get('buffers', [])
        if len(buffers) != 1 or 'uri' in buffers[0]:
            raise ValueError('This intake requires a single embedded buffer')
        self.buffer_length = buffers[0]['byteLength']
        if self.buffer_length > len(self.binary) or len(self.binary) - self.buffer_length > 3:
            raise ValueError('Embedded buffer length mismatch')
        for view in self.doc.get('bufferViews', []):
            if view.get('buffer') != 0 or min(view.get('byteOffset', 0), view['byteLength']) < 0:
                raise ValueError('Invalid buffer view')
            if view.get('byteOffset', 0) + view['byteLength'] > self.buffer_length:
                raise ValueError('Buffer view escapes embedded buffer')
        for image in self.doc.get('images', []):
            if 'uri' in image:
                raise ValueError('External image URIs are not supported by this self-contained intake')
        self.cache = {}

    def layout(self, index):
        accessors = self.doc.get('accessors', [])
        if not isinstance(index, int) or index < 0 or index >= len(accessors):
            raise ValueError('Invalid accessor reference')
        accessor = accessors[index]
        if 'sparse' in accessor or 'bufferView' not in accessor:
            raise ValueError('Sparse/implicit accessors require a different validator')
        formats = {5120: 'b', 5121: 'B', 5122: 'h', 5123: 'H', 5125: 'I', 5126: 'f'}
        widths = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
        component, width = formats[accessor['componentType']], widths[accessor['type']]
        if accessor['type'] == 'MAT4' and accessor['componentType'] != 5126:
            raise ValueError('Only float MAT4 accessors are supported')
        view_id = accessor['bufferView']
        if not isinstance(view_id, int) or not 0 <= view_id < len(self.doc['bufferViews']):
            raise ValueError('Invalid buffer-view reference')
        view = self.doc['bufferViews'][view_id]
        size = struct.calcsize('<' + component * width)
        stride = view.get('byteStride', size)
        relative = accessor.get('byteOffset', 0)
        count = accessor['count']
        if count <= 0 or relative < 0 or stride < size or stride % struct.calcsize(component):
            raise ValueError('Invalid accessor layout')
        if relative + (count - 1) * stride + size > view['byteLength']:
            raise ValueError('Accessor escapes its buffer view')
        return accessor, view.get('byteOffset', 0) + relative, stride, component, width

    def values(self, index):
        if index not in self.cache:
            accessor, offset, stride, component, width = self.layout(index)
            values = [struct.unpack_from('<' + component * width, self.binary, offset + i * stride)
                      for i in range(accessor['count'])]
            if component == 'f' and any(not math.isfinite(v) for row in values for v in row):
                raise ValueError('Nonfinite accessor data')
            if accessor.get('normalized'):
                if component not in ('b', 'B', 'h', 'H'):
                    raise ValueError('Invalid normalized component type')
                maximum = {'b': 127, 'B': 255, 'h': 32767, 'H': 65535}[component]
                values = [tuple(max(v / maximum, -1) for v in row) for row in values]
            self.cache[index] = values
        return self.cache[index]

    def world_matrices(self):
        nodes = self.doc.get('nodes', [])
        parents = {}
        for i, node in enumerate(nodes):
            for child in node.get('children', []):
                if not isinstance(child, int) or not 0 <= child < len(nodes) or child in parents:
                    raise ValueError('Invalid or multiply parented node')
                parents[child] = i
        world, visiting = {}, set()
        def visit(i):
            if i in visiting:
                raise ValueError('Cyclic node graph')
            if i not in world:
                visiting.add(i)
                local = local_matrix(nodes[i])
                world[i] = multiply(visit(parents[i]), local) if i in parents else local
                visiting.remove(i)
            return world[i]
        for i in range(len(nodes)):
            visit(i)
        if any(not math.isfinite(v) for m in world.values() for row in m for v in row):
            raise ValueError('Nonfinite node transform')
        return world, parents

    def audit(self):
        doc = self.doc
        world, parents = self.world_matrices()
        for node in doc.get('nodes', []):
            if 'mesh' in node and (not isinstance(node['mesh'], int) or not 0 <= node['mesh'] < len(doc.get('meshes', []))):
                raise ValueError('Invalid node mesh reference')
        for i in range(len(doc.get('accessors', []))):
            self.values(i)
        report = {'sha256': hashlib.sha256(self.payload).hexdigest(), 'bytes': len(self.payload),
                  'meshes': len(doc.get('meshes', [])), 'skins': len(doc.get('skins', [])),
                  'joint_counts': [len(s['joints']) for s in doc.get('skins', [])],
                  'animation_names': [a.get('name', '(unnamed)') for a in doc.get('animations', [])],
                  'triangles': 0, 'errors': [], 'scope': 'limited-embedded-glb-and-rest-bind-check',
                  'unreal_verified': False, 'combat_ready': False}
        for mesh in doc.get('meshes', []):
            for primitive in mesh['primitives']:
                positions = self.values(primitive['attributes']['POSITION'])
                if any(len(self.values(index)) != len(positions) for index in primitive['attributes'].values()):
                    raise ValueError('Mesh attribute vertex counts differ')
                if self.doc['accessors'][primitive['attributes']['POSITION']]['type'] != 'VEC3':
                    raise ValueError('POSITION accessor must be VEC3')
                indices = self.values(primitive['indices']) if 'indices' in primitive else [(i,) for i in range(len(positions))]
                if any(len(v) != 1 or not isinstance(v[0], int) or not 0 <= v[0] < len(positions) for v in indices):
                    raise ValueError('Mesh index outside POSITION accessor')
                if primitive.get('mode', 4) != 4 or len(indices) % 3:
                    raise ValueError('This intake requires TRIANGLES primitives')
                report['triangles'] += len(indices) // 3
        referenced = set()
        for node_id, node in enumerate(doc.get('nodes', [])):
            if 'skin' not in node:
                continue
            skin_id = node['skin']
            if not isinstance(skin_id, int) or not 0 <= skin_id < len(doc.get('skins', [])) or 'mesh' not in node:
                raise ValueError('Skinned node requires valid skin and mesh references')
            referenced.add(skin_id)
            skin = doc['skins'][skin_id]
            joints = skin['joints']
            if not joints or len(set(joints)) != len(joints) or any(j not in world for j in joints):
                raise ValueError('Invalid joint references')
            roots = []
            for joint in joints:
                while joint in parents:
                    joint = parents[joint]
                roots.append(joint)
            if len(set(roots)) != 1:
                report['errors'].append('Skin joints have no common hierarchy root')
            binds = self.values(skin['inverseBindMatrices']) if 'inverseBindMatrices' in skin else [flatten(IDENTITY)] * len(joints)
            if len(binds) < len(joints) or any(len(row) != 16 for row in binds):
                raise ValueError('Inverse-bind accessor count/type mismatch')
            residual = max(abs(multiply(world[j], matrix(binds[k]))[r][c] - world[node_id][r][c])
                           for k, j in enumerate(joints) for r in range(4) for c in range(4))
            report['rest_bind_max_error'] = max(report.get('rest_bind_max_error', 0), residual)
            if residual > 5e-4:
                report['errors'].append('Rest-pose inverse-bind matrices do not preserve mesh placement')
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                attributes = primitive['attributes']
                joint_rows = self.values(attributes['JOINTS_0'])
                weight_rows = self.values(attributes['WEIGHTS_0'])
                positions = self.values(attributes['POSITION'])
                if len(joint_rows) != len(positions) or len(weight_rows) != len(positions):
                    raise ValueError('Skin accessor vertex counts differ')
                for ids, weights in zip(joint_rows, weight_rows):
                    if len(ids) != 4 or len(weights) != 4 or any(not isinstance(i, int) or not 0 <= i < len(joints) for i in ids):
                        raise ValueError('Invalid vertex joint indices')
                    if any(w < 0 for w in weights) or abs(sum(weights) - 1) > 1e-4:
                        raise ValueError('Skin weights must be nonnegative and sum to one')
        for skin_id in range(len(doc.get('skins', []))):
            if skin_id not in referenced:
                report['errors'].append('Skin %d is not attached to a mesh node' % skin_id)
        for animation in doc.get('animations', []):
            for sampler in animation['samplers']:
                times = self.values(sampler['input'])
                if any(len(t) != 1 or t[0] < 0 for t in times) or any(a[0] >= b[0] for a, b in zip(times, times[1:])):
                    raise ValueError('Animation input times are invalid')
        report['verified'] = report['meshes'] > 0 and not report['errors']
        return report

    def encode(self):
        document = json.dumps(self.doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        document += b' ' * (-len(document) % 4)
        binary = bytes(self.binary)
        binary += b'\0' * (-len(binary) % 4)
        return (struct.pack('<4sII', b'glTF', 2, 28 + len(document) + len(binary))
                + struct.pack('<II', len(document), 0x4E4F534A) + document
                + struct.pack('<II', len(binary), 0x004E4942) + binary)


def repair_single_skin(payload):
    glb = GLB(payload)
    meshes = [(i, n) for i, n in enumerate(glb.doc.get('nodes', [])) if 'mesh' in n]
    if len(glb.doc.get('skins', [])) != 1 or len(meshes) != 1:
        raise ValueError('Repair requires exactly one skin and one mesh node; ownership must not be guessed')
    node_id, node = meshes[0]
    if 'skin' in node and node['skin'] != 0:
        raise ValueError('Mesh is bound to another skin')
    skin = glb.doc['skins'][0]
    world, _ = glb.world_matrices()
    accessor, offset, stride, component, width = glb.layout(skin['inverseBindMatrices'])
    if component != 'f' or width != 16 or accessor['count'] != len(skin['joints']):
        raise ValueError('Repair requires one float MAT4 per joint')
    node['skin'] = 0
    for i, joint in enumerate(skin['joints']):
        bind = multiply(inverse(world[joint]), world[node_id])
        struct.pack_into('<16f', glb.binary, offset + i * stride, *flatten(bind))
    repaired = glb.encode()
    if not GLB(repaired).audit()['verified']:
        raise ValueError('Repaired source failed its bind-pose gate')
    return repaired


def normalize_spec(spec):
    if spec is None:
        return None
    if not isinstance(spec, dict):
        raise ValueError('Import spec must be an object')
    if 'schema_version' not in spec:
        entries = {name: {'required_classes': classes} for name, classes in spec.items()}
    else:
        if spec.get('schema_version') != 2 or not isinstance(spec.get('assets'), dict) or not spec['assets']:
            raise ValueError('Invalid versioned source contract')
        entries = spec['assets']
        for entry in entries.values():
            digest = entry.get('sha256') if isinstance(entry, dict) else None
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                raise ValueError('Versioned source contracts require SHA-256 per asset')
    for name, entry in entries.items():
        if not isinstance(name, str) or not isinstance(entry, dict):
            raise ValueError('Invalid source contract entry')
        classes = entry.get('required_classes')
        if not isinstance(classes, list) or any(not isinstance(v, str) for v in classes):
            raise ValueError('Required classes must be an array of names')
    return entries


def check_source(payload, entry=None):
    if entry and 'sha256' in entry and hashlib.sha256(payload).hexdigest() != entry['sha256']:
        raise ValueError('Source SHA-256 differs from the pinned intake snapshot')
    report = GLB(payload).audit()
    if not report['verified']:
        raise ValueError('; '.join(report['errors']))
    return report
