"""CHAR-023 contract tests: source-free synthetic geometry, never game QA."""
import unittest
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / "tools" / "assetforge"))
from char023_weapon_review import (index_components, partition_faces, choose_grip,
    make_partition, make_body_only, make_rigid_weapon, accessor_array,
    rotation_y, socket_offset)

def fixture():
    p=np.array([[-.4,.5,0],[-.4,.4,0],[-.3,.4,0],
                [-.2,.42,.04],[-.2,.34,.06],[-.18,.36,.06],
                [-.1,.2,.2],[-.05,.02,.34],[-.03,.04,.35]],dtype='<f4')
    n=np.tile(np.array([[0,0,1]],dtype='<f4'),(len(p),1))
    uv=np.zeros((len(p),2),dtype='<f4')
    f=np.array([[0,1,2],[3,4,5],[6,7,8]],dtype='<u2')
    views=[];access=[];blob=bytearray()
    for data,typ,target in [(p,'VEC3',34962),(n,'VEC3',34962),(uv,'VEC2',34962),(f,'SCALAR',34963)]:
        start=len(blob);blob+=data.tobytes();vi=len(views)
        views.append(dict(buffer=0,byteOffset=start,byteLength=data.nbytes,target=target))
        ac=dict(bufferView=vi,componentType=5123 if data.dtype==np.dtype('uint16') else 5126,count=data.size if typ=='SCALAR' else len(data),type=typ)
        access.append(ac)
    doc=dict(asset=dict(version='2.0'),scene=0,scenes=[dict(nodes=[0])],
        nodes=[dict(name='hero',mesh=0,skin=0)],
        meshes=[dict(primitives=[dict(attributes={'POSITION':0,'NORMAL':1,'TEXCOORD_0':2,'JOINTS_0':0,'WEIGHTS_0':1},indices=3,material=0)])],
        materials=[dict(name='original')],skins=[dict(joints=[0])],animations=[dict(name='idle')],
        accessors=access,bufferViews=views,buffers=[dict(byteLength=len(blob))])
    return doc,bytes(blob),f

class WeaponReview(unittest.TestCase):
    def test_index_components_deterministic(self):
        _,_,f=fixture()
        labels=index_components(9,f)
        self.assertEqual(labels.tolist(), [0,0,0,1,1,1,2,2,2])
    def test_partition_lossless(self):
        _,_,f=fixture();lab=index_components(9,f)
        m=partition_faces(f,lab,{2},{1})
        self.assertEqual(tuple(int(m[k].sum()) for k in ('body','guard','blade')),(1,1,1))
        self.assertTrue(np.all(m['body']|m['guard']|m['blade']))
    def test_reject_missing_component(self):
        _,_,f=fixture();lab=index_components(9,f)
        with self.assertRaises(ValueError):partition_faces(f,lab,{99},{1})
    def test_reject_overlap_components(self):
        _,_,f=fixture();lab=index_components(9,f)
        with self.assertRaises(ValueError):partition_faces(f,lab,{1},{1})
    def test_grip_guard_upper_section(self):
        p=np.array([[-.21,.4,.04],[-.2,.42,.04],[-.19,.38,.05],[-.2,.3,.07]])
        np.testing.assert_allclose(choose_grip(p,min_height=.39),[-.205,.41,.04])
    def test_partition_keeps_original_binary_and_attributes(self):
        d,b,f=fixture();m=partition_faces(f,index_components(9,f),{2},{1})
        x,c=make_partition(d,b,m)
        self.assertEqual(c[:len(b)],b)
        self.assertEqual(x['meshes'][0]['primitives'][1]['attributes'],d['meshes'][0]['primitives'][0]['attributes'])
        self.assertEqual(sum(x['accessors'][p['indices']]['count'] for p in x['meshes'][0]['primitives']),9)
    def test_body_only_removes_weapon_faces_not_skin(self):
        d,b,f=fixture();m=partition_faces(f,index_components(9,f),{2},{1})
        x,c=make_body_only(d,b,m['body'])
        self.assertEqual(x['skins'],d['skins']);self.assertEqual(x['animations'],d['animations'])
        self.assertEqual(accessor_array(x,c,x['meshes'][0]['primitives'][0]['indices']).reshape(-1,3).tolist(),[[0,1,2]])
    def test_rigid_weapon_preserves_world_shape(self):
        d,b,f=fixture();m=partition_faces(f,index_components(9,f),{2},{1});pivot=np.array([-.2,.42,.04])
        x,c=make_rigid_weapon(d,b,m,pivot)
        self.assertNotIn('skins',x);self.assertNotIn('animations',x)
        self.assertEqual(len(x['meshes'][0]['primitives']),2)
        world=np.asarray(x['nodes'][0]['translation']);g=x['meshes'][0]['primitives']
        p=accessor_array(x,c,g[0]['attributes']['POSITION'])+world
        np.testing.assert_allclose(p,accessor_array(d,b,0)[np.unique(f[1:])],atol=3e-8)
    def test_socket_offset_and_360_invariant(self):
        joint=np.array([-.43,.48,0]);grip=np.array([-.2,.42,.04]);o=socket_offset(joint,grip)
        for deg in [0,90,180,270,360]:
            R=rotation_y(deg);got=joint+R@o
            np.testing.assert_allclose(np.linalg.norm(got-joint),np.linalg.norm(o),atol=1e-12)
        np.testing.assert_allclose(joint+rotation_y(360)@o,grip,atol=1e-12)
    def test_reject_empty_guard(self):
        with self.assertRaises(ValueError):choose_grip(np.array([[0,.1,0]],float),min_height=.4)

if __name__=='__main__':unittest.main()
