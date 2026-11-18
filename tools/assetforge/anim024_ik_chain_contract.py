"""ANIM-024: fail-closed source IK chain contract, NO Unreal asset mutation.

The original-user GLBs are not checked into the repo. The separate user
handoff includes expanded source-space visuals, mock UE installer and tests.
"""
import hashlib, json, math, struct
from pathlib import Path

PINS={'body':'2fc95a46ba69f23c4365390bea277f185bc83e187286140d56d22aa080e0780d',
      'preview':'b5dc669cb81b81f93f3b7c2131446437823d0d5ae1cc5a4be85d47d2eb1a0015'}
PARENT={'root':None,'pelvis':'root','spine':'pelvis','chest':'spine','neck':'chest','head':'neck',
        'upper_arm_L':'chest','lower_arm_L':'upper_arm_L','hand_L':'lower_arm_L',
        'upper_arm_R':'chest','lower_arm_R':'upper_arm_R','hand_R':'lower_arm_R',
        'thigh_L':'pelvis','calf_L':'thigh_L','foot_L':'calf_L',
        'thigh_R':'pelvis','calf_R':'thigh_R','foot_R':'calf_R'}
CHAINS={'Root':('root','pelvis'),'Spine':('pelvis','chest'),'Head':('neck','head'),
        'LeftArm':('upper_arm_L','hand_L'),'RightArm':('upper_arm_R','hand_R'),
        'LeftLeg':('thigh_L','foot_L'),'RightLeg':('thigh_R','foot_R')}
def read_glb(path):
    b=Path(path).read_bytes()
    if len(b)<28 or struct.unpack_from('<4sII',b)!=(b'glTF',2,len(b)):
        raise ValueError('Unrecognized GLB v2 header')
    n,t=struct.unpack_from('<I4s',b,12)
    if t!=b'JSON' or 20+n+8>len(b):raise ValueError('Invalid JSON chunk')
    m,v=struct.unpack_from('<I4s',b,20+n)
    if v!=b'BIN\x00' or 20+n+8+m!=len(b):raise ValueError('Invalid BIN chunk')
    d=json.loads(b[20:20+n])
    if d.get('asset',{}).get('version')!='2.0':raise ValueError('Not glTF 2.0')
    return d,hashlib.sha256(b).hexdigest()

def source_skeleton(doc):
    skins=doc.get('skins',[])
    nodes=doc.get('nodes',[])
    if len(skins)!=1 or len(skins[0].get('joints',[]))!=18:raise ValueError('Not pinned 18-joint skin')
    ids=skins[0]['joints']
    if len(set(ids))!=18 or any(type(i)!=int or not 0<=i<len(nodes) for i in ids):
        raise ValueError('Invalid skin joints')
    names={i:nodes[i].get('name') for i in ids}
    if len(set(names.values()))!=18 or set(names.values())!=set(PARENT):
        raise ValueError('Bone names differ from source signature')
    node_parents={}
    for i,n in enumerate(nodes):
        for child in n.get('children',[]):
            if child in node_parents or not 0<=child<len(nodes):
                raise ValueError('Invalid node parent')
            node_parents[child]=i
    local={}
    for i,name in names.items():
        parent=node_parents.get(i)
        if (names.get(parent) if parent is not None else None)!=PARENT[name]:
            raise ValueError('Wrong source bone hierarchy')
        n=nodes[i]
        if 'matrix' in n or n.get('rotation',[0,0,0,1])!=[0,0,0,1] or n.get('scale',[1,1,1])!=[1,1,1]:
            raise ValueError('Unexpected non-identity reference transform')
        v=n.get('translation',[0,0,0])
        if len(v)!=3 or not all(math.isfinite(float(x)) for x in v):raise ValueError('Invalid translation')
        local[name]=tuple(float(x) for x in v)
    world={}
    def calc(name,trail=()):
        if name in trail:raise ValueError('Bone cycle')
        if name not in world:
            parent=PARENT[name]
            root=calc(parent,trail+(name,)) if parent else (0.,0.,0.)
            world[name]=tuple(a+b for a,b in zip(root,local[name]))
        return world[name]
    for name in PARENT:calc(name)
    return {'joint_count':18,'parents':dict(PARENT),'local':local,'world':world}

def source_path(start,end):
    if start not in PARENT or end not in PARENT:raise ValueError('Unknown chain bones')
    path=[end]
    while path[-1]!=start:
        parent=PARENT[path[-1]]
        if parent is None or parent in path:raise ValueError('Broken chain ancestry')
        path.append(parent)
    return list(reversed(path))

def build_source_plan(body_path,preview_path):
    d,ds=read_glb(body_path);a,ahs=read_glb(preview_path)
    if ds!=PINS['body'] or ahs!=PINS['preview']:
        raise ValueError('Actual GLB fingerprint mismatch; no automated rig mapping')
    s=source_skeleton(d);t=source_skeleton(a)
    if s!=t:raise ValueError('Preview and source joint bind trees differ')
    out={}
    for name,(start,end) in CHAINS.items():
        path=source_path(start,end)
        length=sum(math.dist(s['world'][x],s['world'][y]) for x,y in zip(path,path[1:]))
        if length<.05:raise ValueError('Degenerate retarget source chain')
        out[name]={'start':start,'end':end,'bones':path,'length_source_units':round(length,9)}
    if abs(out['LeftArm']['length_source_units']-out['RightArm']['length_source_units'])>1e-5:
        raise ValueError('Asymmetric source arm bind chains')
    if abs(out['LeftLeg']['length_source_units']-out['RightLeg']['length_source_units'])>1e-5:
        raise ValueError('Asymmetric source leg bind chains')
    return {'id':'ANIM-024-IK-SOURCE-REVIEW','source_sha256':PINS,'joint_count':18,
            'retarget_root':'pelvis','root_bone':'root','chains':out,
            'source_chain_gate':'PASS','imported_skeletal_mesh':'UNVERIFIED',
            'IKRig_asset':'NOT_CREATED','IKRetargeter_asset':'NOT_CREATED',
            'production_87_bone_rig':'NOT_MET','toe_bones':'ABSENT',
            'release_ready':False}
