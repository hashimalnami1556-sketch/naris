"""Source-only ANIM-024 IK chain tests. Real GLBs live in user's handoff."""
import hashlib, json, os, struct, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'/'assetforge'))
from anim024_ik_chain_contract import PINS,PARENT,CHAINS,read_glb,source_skeleton,source_path,build_source_plan

def fixture():
    offsets={'root':(0,.05,0),'pelvis':(0,.31,0),'spine':(0,.18,0),
      'chest':(0,.13,0),'neck':(0,.13,0),'head':(0,.11,0),
      'upper_arm_L':(-.2,.02,0),'lower_arm_L':(-.14,-.12,0),'hand_L':(-.09,-.09,0),
      'upper_arm_R':(.2,.02,0),'lower_arm_R':(.14,-.12,0),'hand_R':(.09,-.09,0),
      'thigh_L':(-.13,-.08,0),'calf_L':(-.01,-.14,0),'foot_L':(0,-.11,.06),
      'thigh_R':(.13,-.08,0),'calf_R':(.01,-.14,0),'foot_R':(0,-.11,.06)}
    names=list(PARENT)
    nodes=[{'name':name,'translation':list(offsets[name])} for name in names]
    for i,name in enumerate(names):
        if PARENT[name]:nodes[names.index(PARENT[name])].setdefault('children',[]).append(i)
    return {'asset':{'version':'2.0'},'nodes':nodes,'skins':[{'joints':list(range(18))}]}

def bytes_glb(doc):
    raw=json.dumps(doc,separators=(',',':')).encode()
    raw+=b' '*((-len(raw))%4)
    binary=b'\x00'*4
    size=12+8+len(raw)+8+len(binary)
    return struct.pack('<4sII',b'glTF',2,size)+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(binary),b'BIN\x00')+binary

class SourceIKContracts(unittest.TestCase):
    def test_synthetic_18_joints_and_parent_mapping(self):
        s=source_skeleton(fixture())
        self.assertEqual(s['joint_count'],18)
        self.assertEqual(s['parents']['hand_L'],'lower_arm_L')
    def test_neck_head_chain(self):
        self.assertEqual(source_path('neck','head'),['neck','head'])
    def test_leg_chain_ancestor(self):
        self.assertEqual(source_path('thigh_R','foot_R'),['thigh_R','calf_R','foot_R'])
    def test_cross_limb_rejected(self):
        with self.assertRaises(ValueError):source_path('thigh_L','hand_R')
    def test_extra_bone_rejected(self):
        d=fixture();d['skins'][0]['joints'].append(18)
        with self.assertRaises(ValueError):source_skeleton(d)
    def test_wrong_parent_rejected(self):
        d=fixture();d['nodes'][7]['children'].remove(8);d['nodes'][3].setdefault('children',[]).append(8)
        with self.assertRaises(ValueError):source_skeleton(d)
    def test_nonidentity_bind_rotation_rejected(self):
        d=fixture();d['nodes'][8]['rotation']=[0,.1,0,.995]
        with self.assertRaises(ValueError):source_skeleton(d)
    def test_temp_glb_roundtrip(self):
        d=fixture();raw=bytes_glb(d)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'fixture.glb';p.write_bytes(raw)
            got,digest=read_glb(p)
        self.assertEqual(got,d);self.assertEqual(digest,hashlib.sha256(raw).hexdigest())
    def test_synthetic_matched_pair_yields_seven_review_chains(self):
        raw=bytes_glb(fixture());digest=hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'hero.glb';p.write_bytes(raw)
            with patch.dict(PINS,{'body':digest,'preview':digest}):
                q=build_source_plan(p,p)
        self.assertEqual(len(q['chains']),7)
        self.assertEqual(q['retarget_root'],'pelvis')
        self.assertFalse(q['release_ready'])
        self.assertEqual(q['IKRig_asset'],'NOT_CREATED')
    def test_tampered_source_digest_blocks_plan(self):
        raw=bytes_glb(fixture())
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'hero.glb';p.write_bytes(raw)
            with self.assertRaises(ValueError):build_source_plan(p,p)
    def test_real_file_when_provided(self):
        body=os.environ.get('ANIM024_BODY_GLTF')
        preview=os.environ.get('ANIM024_PREVIEW_GLTF')
        if not body or not preview:self.skipTest('Original user GLB not stored in GitHub CI')
        q=build_source_plan(Path(body),Path(preview))
        self.assertEqual(len(q['chains']),7)
        self.assertEqual(q['source_chain_gate'],'PASS')
if __name__=='__main__':unittest.main()
