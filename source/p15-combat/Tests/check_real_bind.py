"""Independent NumPy CPU skinning check on the attached translation-only prototype."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('p15_cpu_bind_check', ROOT / 'Unreal/source_assets.py')
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def verify(original, fixed):
    raw, repaired = S.GLB(Path(original).read_bytes()), S.GLB(Path(fixed).read_bytes())
    node_id = next(i for i, n in enumerate(repaired.doc['nodes']) if 'mesh' in n)
    expected_doc = copy.deepcopy(raw.doc)
    expected_doc['nodes'][node_id]['skin'] = 0
    if expected_doc != repaired.doc:
        raise ValueError('The repair changed metadata beyond the mesh skin binding')
    skin = repaired.doc['skins'][0]
    _, offset, stride, _, _ = raw.layout(skin['inverseBindMatrices'])
    affected = set(j for i in range(len(skin['joints'])) for j in range(offset+i*stride, offset+i*stride+64))
    if len(raw.binary) != len(repaired.binary) or any(a != b for i, (a,b) in enumerate(zip(raw.binary, repaired.binary)) if i not in affected):
        raise ValueError('The repair modified vertex, texture, weight or animation bytes')
    nodes = repaired.doc['nodes']
    parents = {child: i for i, node in enumerate(nodes) for child in node.get('children', [])}
    # This independent check deliberately supports only the actual translation-only source.
    if any('matrix' in node or node.get('rotation', [0,0,0,1]) != [0,0,0,1]
           or node.get('scale', [1,1,1]) != [1,1,1] for node in nodes):
        raise ValueError('CPU fixture is no longer translation-only; update the independent oracle')
    def world(i):
        result = np.eye(4)
        while True:
            result[:3,3] += nodes[i].get('translation', [0,0,0])
            if i not in parents:
                return result
            i = parents[i]
    attrs = repaired.doc['meshes'][nodes[node_id]['mesh']]['primitives'][0]['attributes']
    positions = np.array(repaired.values(attrs['POSITION']), dtype=np.float64)
    joints = np.array(repaired.values(attrs['JOINTS_0']), dtype=np.int64)
    weights = np.array(repaired.values(attrs['WEIGHTS_0']), dtype=np.float64)
    inverse_binds = [np.array(values).reshape((4,4), order='F') for values in repaired.values(skin['inverseBindMatrices'])]
    transforms = np.stack([world(joint) @ bind for joint, bind in zip(skin['joints'], inverse_binds)])
    vertices = np.column_stack([positions, np.ones(len(positions))])
    deformed = np.zeros_like(vertices)
    for influence in range(4):
        transformed = np.einsum('nij,nj->ni', transforms[joints[:,influence]], vertices)
        deformed += weights[:,influence,None] * transformed
    expected = vertices @ world(node_id).T
    error = float(np.max(np.abs(deformed - expected)))
    if error > 1e-6:
        raise ValueError('Rest skinning displaced mesh vertices: ' + str(error))
    return {'verified': True, 'scope': 'independent-rest-pose-cpu-skinning',
            'vertices_checked': len(positions), 'max_coordinate_error': error,
            'preserved_non_bind_binary_bytes': True, 'preserved_original_animation': True,
            'unreal_verified': False, 'animation_visual_quality_verified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', required=True)
    parser.add_argument('--fixed', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args()
    report = verify(args.original, args.fixed)
    Path(args.report).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
