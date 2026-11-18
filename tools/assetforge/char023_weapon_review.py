"""CHAR-023: audited, non-destructive sword extraction from a pinned GLB.
Review only: visual approval, engine Socket, game tests and UE build remain open.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, struct
from pathlib import Path
import numpy as np

EXPECTED_SOURCE_SHA256 = 'a9389d433d31886c1d4273e6acda0950ca6657fac20338063b9bb643ca95fdd9'
BLADE_COMPONENTS = frozenset(range(86, 93))
GUARD_COMPONENTS = frozenset((71, 75, 78, 80, 82, 84))

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_glb(path: Path):
    b = Path(path).read_bytes()
    if len(b) < 28 or struct.unpack_from('<4sII', b) != (b'glTF', 2, len(b)):
        raise ValueError('GLB header mismatch')
    jn, jt = struct.unpack_from('<I4s', b, 12)
    if jt != b'JSON' or (20 + jn + 8) > len(b):
        raise ValueError('Invalid GLB JSON chunk')
    bn, bt = struct.unpack_from('<I4s', b, 20 + jn)
    if bt != b'BIN\x00' or 20 + jn + 8 + bn != len(b):
        raise ValueError('Invalid GLB BIN chunk')
    return json.loads(b[20:20 + jn]), b[20 + jn + 8:]

def write_glb(path: Path, doc: dict, blob: bytes):
    j = json.dumps(doc, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    j += b' ' * ((-len(j)) % 4)
    blob += b'\x00' * ((-len(blob)) % 4)
    payload = struct.pack('<I4s', len(j), b'JSON') + j + struct.pack('<I4s', len(blob), b'BIN\x00') + blob
    Path(path).write_bytes(struct.pack('<4sII', b'glTF', 2, len(payload) + 12) + payload)

def accessor_array(doc: dict, blob: bytes, idx: int) -> np.ndarray:
    a = doc['accessors'][idx]
    v = doc['bufferViews'][a['bufferView']]
    if 'sparse' in a or v.get('buffer', 0) != 0:
        raise ValueError('Sparse or external accessors unsupported')
    dt = np.dtype({5126:'<f4', 5121:'u1', 5123:'<u2', 5125:'<u4'}[a['componentType']])
    width = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4, 'MAT4':16}[a['type']]
    stride = v.get('byteStride', width * dt.itemsize)
    offset = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    if offset + (a['count'] - 1) * stride + width * dt.itemsize > len(blob):
        raise ValueError('Accessor beyond binary payload')
    return np.ndarray((a['count'],width), dtype=dt, buffer=blob, offset=offset,
                      strides=(stride,dt.itemsize))

def index_components(vertex_count: int, faces: np.ndarray) -> np.ndarray:
    f = np.asarray(faces)
    if vertex_count < 1 or f.ndim != 2 or f.shape[1] != 3 or f.dtype.kind not in 'iu' or len(f) < 1:
        raise ValueError('Invalid topology')
    if f.min() < 0 or f.max() >= vertex_count:
        raise ValueError('Out-of-range vertex index')
    parent = np.arange(vertex_count, dtype=np.int32)
    def root(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = int(parent[v])
        return v
    for a,b,c in f.tolist():
        x, y, z = root(a), root(b), root(c)
        parent[y] = x
        parent[z] = x
    labels = np.empty(vertex_count, np.int32)
    component_by_root = {}
    for i in range(vertex_count):
        r = root(i)
        if r not in component_by_root:
            component_by_root[r] = len(component_by_root)
        labels[i] = component_by_root[r]
    return labels

def partition_faces(faces: np.ndarray, component_ids: np.ndarray,
                    blade_components, guard_components):
    f = np.asarray(faces)
    labels = np.asarray(component_ids)
    blade_components, guard_components = set(blade_components), set(guard_components)
    if blade_components & guard_components or not blade_components or not guard_components:
        raise ValueError('Component selection overlaps or is empty')
    present = set(np.unique(labels[f]).tolist())
    if not blade_components.issubset(present) or not guard_components.issubset(present):
        raise ValueError('Selected components missing in file')
    if not np.all(labels[f] == labels[f[:,0],None]):
        raise ValueError('Faces cross component boundaries')
    fl = labels[f[:,0]]
    blade = np.isin(fl,sorted(blade_components))
    guard = np.isin(fl,sorted(guard_components))
    body = ~(blade|guard)
    if not body.any() or not blade.any() or not guard.any():
        raise ValueError('Unexpected empty geometry partition')
    return {'body':body, 'guard':guard, 'blade':blade}

def choose_grip(guard_positions: np.ndarray, min_height=0.4) -> np.ndarray:
    p = np.asarray(guard_positions,dtype=float)
    if p.ndim != 2 or p.shape[1] != 3 or not np.isfinite(p).all() or not math.isfinite(min_height):
        raise ValueError('Invalid grip geometry')
    near_hilt = p[p[:,1] >= min_height]
    if not len(near_hilt):
        raise ValueError('No upper guard/handle samples')
    return np.median(near_hilt,axis=0)

def append_accessor(doc: dict, binary: bytearray, data: np.ndarray,
                    semantic: str, target: int) -> int:
    arr = np.ascontiguousarray(data)
    if semantic == 'INDEX':
        arr = arr.reshape(-1, 1)
    elif arr.ndim == 1:
        arr = arr[:,None]
    if arr.ndim != 2 or not len(arr):
        raise ValueError('Empty attribute')
    typ = {1:'SCALAR',2:'VEC2',3:'VEC3',4:'VEC4'}[arr.shape[1]]
    component = {np.dtype('<f4'):5126,np.dtype('<u2'):5123,np.dtype('<u4'):5125}[arr.dtype]
    binary.extend(b'\0'*((-len(binary))%4))
    start = len(binary)
    binary.extend(arr.tobytes())
    view_id = len(doc['bufferViews'])
    doc['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':arr.nbytes,'target':target})
    accessor = {'bufferView':view_id,'componentType':component,'count':len(arr),'type':typ}
    if semantic in ('POSITION','INDEX'):
        accessor['min'] = [float(v) if component == 5126 else int(v) for v in arr.min(axis=0)]
        accessor['max'] = [float(v) if component == 5126 else int(v) for v in arr.max(axis=0)]
    doc['accessors'].append(accessor)
    doc['buffers'][0]['byteLength'] = len(binary)
    return len(doc['accessors'])-1

def source_faces(doc: dict, blob: bytes):
    if len(doc.get('meshes',[])) != 1 or len(doc['meshes'][0]['primitives']) != 1:
        raise ValueError('One primitive required')
    pr = doc['meshes'][0]['primitives'][0]
    f = accessor_array(doc,blob,pr['indices']).reshape(-1,3)
    return pr, f

def make_partition(doc: dict, blob: bytes, masks):
    d = copy.deepcopy(doc);b = bytearray(blob)
    primitive,faces = source_faces(doc,blob)
    out = []
    for name in ('body','guard','blade'):
        ids = append_accessor(d,b,np.asarray(faces[masks[name]],dtype='<u2'), 'INDEX',34963)
        p = copy.deepcopy(primitive);p['indices'] = ids
        p['extras'] = {'naris_section':name.upper()+'_REVIEW','production_approved':False}
        out.append(p)
    d['meshes'][0]['primitives'] = out
    return d, bytes(b)

def make_body_only(doc: dict, blob: bytes, body_mask):
    d = copy.deepcopy(doc);b = bytearray(blob)
    primitive,faces = source_faces(doc,blob)
    ids = append_accessor(d,b,np.asarray(faces[body_mask],dtype='<u2'), 'INDEX',34963)
    p = copy.deepcopy(primitive);p['indices'] = ids
    p['extras'] = {'naris_section':'BODY_REVIEW_WITHOUT_WEAPON_CANDIDATES','production_approved':False}
    d['meshes'][0]['primitives'] = [p]
    return d,bytes(b)

def make_rigid_weapon(doc: dict, blob: bytes, masks, grip_pivot: np.ndarray):
    d = copy.deepcopy(doc);b=bytearray(blob)
    primitive, faces = source_faces(doc,blob)
    selected = masks['guard']|masks['blade']
    verts = np.unique(faces[selected].ravel())
    if len(verts)>65535:
        raise ValueError('Uint16 weapon candidate cannot exceed 65,535 vertices')
    pivot = np.asarray(grip_pivot,dtype=float)
    if pivot.shape!=(3,) or not np.isfinite(pivot).all():
        raise ValueError('Invalid pivot')
    attrs = {}
    for sem,kind in [('POSITION','POSITION'),('NORMAL','NORMAL'),('TEXCOORD_0','UV')]:
        data = accessor_array(doc,blob,primitive['attributes'][sem])[verts].copy().astype('<f4')
        if sem=='POSITION':data -= pivot.astype('<f4')
        attrs[sem] = append_accessor(d,b,data,kind,34962)
    out=[]
    for name in ('guard','blade'):
        inds = np.searchsorted(verts, faces[masks[name]]).astype('<u2')
        ids = append_accessor(d,b,inds,'INDEX',34963)
        p = {'attributes':attrs,'indices':ids,'material':primitive['material'],
             'extras':{'naris_section':name.upper()+'_REVIEW','production_approved':False}}
        out.append(p)
    d['meshes']=[{'name':'NARIS_Weapon_OriginalGeometry_REVIEW','primitives':out}]
    d['nodes']=[{'name':'WeaponCandidate_PivotAtGrip_REVIEW','mesh':0,'translation':pivot.tolist()}]
    d['scenes']=[{'name':'WeaponCandidate_Review','nodes':[0]}]
    d['scene']=0
    d.pop('skins',None);d.pop('animations',None)
    d['buffers'][0]['byteLength']=len(b)
    return d,bytes(b)

def socket_offset(hand_bind_location, grip_position):
    hand=np.asarray(hand_bind_location,dtype=float);grip=np.asarray(grip_position,dtype=float)
    if hand.shape!=(3,) or grip.shape!=(3,):raise ValueError('Expected 3D locations')
    return grip-hand

def rotation_y(deg):
    a=np.deg2rad(float(deg));c=np.cos(a);s=np.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])

def bind_joint_world_positions(doc):
    parent={}
    for i,n in enumerate(doc['nodes']):
        for c in n.get('children',[]):
            if c in parent:raise ValueError('Multiple parents')
            parent[c]=i
    cached={}
    def solve(i, stack=()):
        if i in stack:raise ValueError('Cycle in skeleton')
        if i not in cached:
            n=doc['nodes'][i]
            if any(q in n for q in ('matrix','rotation','scale')):
                raise ValueError('Only pinned translation bind joints supported')
            local=np.asarray(n.get('translation',[0,0,0]),dtype=float)
            cached[i]=local+solve(parent[i],stack+(i,)) if i in parent else local
        return cached[i]
    return {n['name']:solve(i) for i,n in enumerate(doc['nodes'])}

def audit_source(doc,blob,source_sha):
    if source_sha!=EXPECTED_SOURCE_SHA256:raise ValueError('Unrecognized source checksum; refusing component assignment')
    if len(doc.get('skins',[]))!=1 or len(doc['skins'][0]['joints'])!=18:
        raise ValueError('Unexpected rig layout')
    p, f = source_faces(doc,blob)
    if len(f)!=49886 or len(accessor_array(doc,blob,p['attributes']['POSITION']))!=32373:
        raise ValueError('Unexpected topology')
    if doc['nodes'][18].get('skin') != 0:
        raise ValueError('Skin correction absent')
    vertex_labels=index_components(32373,f)
    masks=partition_faces(f,vertex_labels,BLADE_COMPONENTS,GUARD_COMPONENTS)
    if len(np.unique(vertex_labels)) != 529 or int(masks['blade'].sum())!=1242 or int(masks['guard'].sum())!=592:
        raise ValueError('Candidate component signature mismatch')
    return p,f,vertex_labels,masks

def scan_image_digests(doc,blob):
    hashes=[]
    for img in doc.get('images',[]):
        v=doc['bufferViews'][img['bufferView']]
        st=v.get('byteOffset',0)
        hashes.append({'name':img.get('name',''),'sha256':sha(blob[st:st+v['byteLength']])})
    return hashes

def audit_outputs(doc,blob,masks,pivot,section,rigid,body):
    src_pr, src_faces=source_faces(doc,blob)
    x, xb=section;y,yb=rigid;z,zb=body
    if xb[:len(blob)]!=blob or yb[:len(blob)]!=blob or zb[:len(blob)]!=blob:
        raise AssertionError('Original payload altered')
    combined=np.zeros(len(src_faces),bool)
    reconstruct=[]
    for name,pr in zip(('body','guard','blade'),x['meshes'][0]['primitives']):
        sub=accessor_array(x,xb,pr['indices']).reshape(-1,3)
        if not np.array_equal(sub,src_faces[masks[name]]):raise AssertionError('Partition mismatches source face IDs')
        if pr['attributes'] != src_pr['attributes'] or pr['material'] != src_pr['material']:
            raise AssertionError('Original render attributes changed')
        combined |= masks[name]
        reconstruct.append(sub)
    if not combined.all() or sum(len(a) for a in reconstruct)!=len(src_faces):raise AssertionError('Not all faces preserved')
    if not np.array_equal(accessor_array(z,zb,z['meshes'][0]['primitives'][0]['indices']).reshape(-1,3),src_faces[masks['body']]):
        raise AssertionError('Skeletal body review subset altered')
    if z['skins']!=doc['skins'] or z['animations']!=doc['animations']:
        raise AssertionError('Source skin/animation modified')
    sel = src_faces[masks['guard']|masks['blade']];used = np.unique(sel)
    wpr=y['meshes'][0]['primitives'];world_pos=accessor_array(y,yb,wpr[0]['attributes']['POSITION']).astype(float)+np.asarray(y['nodes'][0]['translation'])
    src_pos=accessor_array(doc,blob,src_pr['attributes']['POSITION']).astype(float)[used]
    delta=float(np.abs(world_pos-src_pos).max())
    if delta>6e-8:raise AssertionError(f'Weapon static world geometry deviated by {delta}')
    for field in ('NORMAL','TEXCOORD_0'):
        if not np.array_equal(accessor_array(y,yb,wpr[0]['attributes'][field]),accessor_array(doc,blob,src_pr['attributes'][field])[used]):
            raise AssertionError(f'{field} changed')
    for name,pr in zip(('guard','blade'),wpr):
        index=accessor_array(y,yb,pr['indices']).reshape(-1,3).astype(int)
        if not np.array_equal(used[index],src_faces[masks[name]]):raise AssertionError('Weapon index remapping mismatch')
    if scan_image_digests(doc,blob)!=scan_image_digests(y,yb):raise AssertionError('Original JPEG textures altered')
    return {'all_original_faces_accounted_for':True,'texture_digest_unchanged':True,
            'rigged_body_skin_animation_metadata_unchanged':True,'original_bin_prefix_unchanged':True,
            'weapon_world_coordinates_max_deviation_source_units':delta}

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument('--source',type=Path,required=True)
    pa.add_argument('--output-dir',type=Path,required=True)
    args=pa.parse_args()
    src=args.source.resolve();dest=args.output_dir.resolve()
    if not src.is_file() or dest.exists() or dest==src or dest in src.parents:
        raise SystemExit('Missing source or output already exists / path invalid')
    src_data=src.read_bytes();doc,blob=read_glb(src);pr,f,labels,masks=audit_source(doc,blob,sha(src_data))
    pos=accessor_array(doc,blob,pr['attributes']['POSITION']).astype(float)
    joints=accessor_array(doc,blob,pr['attributes']['JOINTS_0']).astype(int)
    weights=accessor_array(doc,blob,pr['attributes']['WEIGHTS_0']).astype(float)
    vertices={name:np.unique(f[masks[name]].ravel()) for name in ('body','blade','guard')}
    grip=choose_grip(pos[vertices['guard']],min_height=.4)
    rest=bind_joint_world_positions(doc)
    offset=socket_offset(rest['hand_L'],grip)
    tip=np.median(pos[labels==92],axis=0)
    axis=tip-grip;axis_length=float(np.linalg.norm(axis));axis/=axis_length
    section=make_partition(doc,blob,masks)
    body=make_body_only(doc,blob,masks['body'])
    weapon=make_rigid_weapon(doc,blob,masks,grip)
    evidence=audit_outputs(doc,blob,masks,grip,section,weapon,body)
    stat={}
    for name in ('blade','guard'):
        v=vertices[name];a=np.zeros(len(doc['skins'][0]['joints']))
        for k in range(4):np.add.at(a,joints[v,k],weights[v,k])
        a=a/len(v)
        stat[name]={doc['nodes'][doc['skins'][0]['joints'][i]]['name']:float(x) for i,x in enumerate(a) if x>0.0001}
    guard_to_hand={k:float(np.linalg.norm(rest[k]-grip)) for k in ('hand_L','hand_R')}
    if guard_to_hand['hand_L']>=guard_to_hand['hand_R']:
        raise AssertionError('Review expected hand_L closer to grip than hand_R')
    drift=max(float(np.linalg.norm(rotation_y(a)@offset)-np.linalg.norm(offset)) for a in (0,90,180,270,360))
    report={'id':'CHAR-023','status':'REVIEW_READY_NOT_PRODUCTION',
      'source_sha256':sha(src_data),'engine_test':'NOT_RUN','ue_socket_creation':'NOT_RUN',
      'source_mesh_unchanged':True,'original_faces':int(len(f)),'index_connected_components':int(len(np.unique(labels))),
      'sections':{name:{'faces':int(masks[name].sum()),'unique_vertices':int(len(vertices[name]))} for name in ('body','guard','blade')},
      'blade_selection_component_ids':sorted(BLADE_COMPONENTS),'guard_selection_component_ids':sorted(GUARD_COMPONENTS),
      'grip_pivot_original_source_units':grip.tolist(),'blade_tip_source_units':tip.tolist(),'blade_forward_axis':axis.tolist(),
      'grip_to_tip_source_units':axis_length,'hand_bind_locations_source_units':{k:rest[k].tolist() for k in ('hand_L','hand_R')},
      'grip_to_hands_source_units':guard_to_hand,'proposed_hand_L_socket_translation_offset_source_units':offset.tolist(),
      'original_skin_weight_influences':stat,'virtual_socket_turn_360_length_error':abs(drift),
      'render_original_geometry_is_preserved_only_in_recombined_review':True,
      'warning':'Guard selection may contain garment/hand geometry; inspect before approving. Static weapon overlap occurs if original skinned sword is not hidden. Transform is in original glTF Y-up coordinates, NOT an Unreal socket asset.',
      'quality_gates':{'original_glb_preserved':'PASS','full_face_partition':'PASS','texture_original':'PASS',
                       'rigid_weapon_pose_geometry':'PASS','runtime_socket_alignment':'NOT_RUN',
                       'physics_capsule_collision':'NOT_RUN','combat_montage':'NOT_RUN',
                       'Unreal_build':'NOT_RUN','network':'NOT_RUN','fps_memory':'NOT_MEASURED'},
      'evidence':evidence,'texture_images_sha256':scan_image_digests(doc,blob),
      'rollback':'Discard independent review outputs; original source GLB and UE project remain untouched.'}
    dest.mkdir(parents=True)
    outputs={'NARIS_CHAR023_SectionReview.glb':section,'NARIS_CHAR023_HeroWithoutWeapon_REVIEW.glb':body,
             'NARIS_CHAR023_RigidWeaponCandidate_REVIEW.glb':weapon}
    for name,(d,b) in outputs.items():
        write_glb(dest/name,d,b)
    report['outputs_sha256']={name:sha((dest/name).read_bytes()) for name in outputs}
    (dest/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (dest/'socket_review.json').write_text(json.dumps({'name':'weapon_l_REVIEW','parent_bone':'hand_L',
      'parent_translation_glTF_Y_up':rest['hand_L'].tolist(),
      'proposed_local_translation_glTF_Y_up':offset.tolist(),
      'grip_position_glTF_Y_up':grip.tolist(),
      'rotation_glTF_Y_up':[0,0,0,1],
      'UNREAL_SOCKET_ASSET_CREATED':False,
      'PRODUCTION_APPROVED':False},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'sections':report['sections'],
      'grip':grip.tolist(),'grip_to_hands':guard_to_hand,'evidence':evidence},indent=2))

if __name__ == '__main__':main()
