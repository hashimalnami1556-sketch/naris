import copy
import json
import struct


def encode(document, binary):
    document = copy.deepcopy(document)
    document['buffers'] = [{'byteLength': len(binary)}]
    raw = json.dumps(document, separators=(',', ':')).encode()
    raw += b' ' * (-len(raw) % 4)
    binary += b'\0' * (-len(binary) % 4)
    return (struct.pack('<4sII', b'glTF', 2, 28 + len(raw) + len(binary))
            + struct.pack('<II', len(raw), 0x4E4F534A) + raw
            + struct.pack('<II', len(binary), 0x004E4942) + binary)


def mesh():
    doc = {'asset': {'version': '2.0'}, 'bufferViews': [{'buffer': 0, 'byteOffset': 0, 'byteLength': 36}],
           'accessors': [{'bufferView': 0, 'componentType': 5126, 'type': 'VEC3', 'count': 3}],
           'meshes': [{'primitives': [{'attributes': {'POSITION': 0}}]}], 'nodes': [{'mesh': 0}]}
    return doc, struct.pack('<9f', 0, 0, 0, 1, 0, 0, 0, 1, 0)


def skinned(bound=False, good_bind=False):
    doc, binary = mesh()
    doc['nodes'] = [{'translation': [.25, .5, 0], 'children': [1, 2]},
                    {'translation': [.5, 0, 0]}, {'mesh': 0}]
    if bound:
        doc['nodes'][2]['skin'] = 0
    data = [
        (struct.pack('<12B', *([0, 0, 0, 0] * 3)), 5121, 'VEC4', 3),
        (struct.pack('<12f', *([1, 0, 0, 0] * 3)), 5126, 'VEC4', 3),
        (struct.pack('<16f', *( [1,0,0,0,0,1,0,0,0,0,1,0,-.5,0,0,1] if good_bind else
                              [1,0,0,-.75,0,1,0,-.5,0,0,1,0,0,0,0,1])), 5126, 'MAT4', 1)]
    for block, component, kind, count in data:
        view = len(doc['bufferViews'])
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(block)})
        doc['accessors'].append({'bufferView': view, 'componentType': component, 'type': kind, 'count': count})
        binary += block
    doc['meshes'][0]['primitives'][0]['attributes'].update(JOINTS_0=1, WEIGHTS_0=2)
    doc['skins'] = [{'joints': [1], 'inverseBindMatrices': 3, 'skeleton': 1}]
    return doc, binary
