"""Synthetic GLBs exercise hierarchy, bind/animation preservation and float times."""
import json,pathlib,struct,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/assets'))
from unify_skin import append,read,unify,values,matrix,mul,inverse,I,globals_at
from check_skin_repair import check

def fixture(path,detached=False):
 d={'asset':{'version':'2.0'},'buffers':[{'byteLength':0}],'bufferViews':[],'accessors':[],'nodes':[{'name':'world','children':[1,2]},{'name':'pelvis','mesh':0,'skin':0,'children':[3]},{'name':'head','mesh':1,'skin':1,'children':[4]},{'name':'J_pelvis'},{'name':'J_head'}],'scenes':[{'nodes':[0]}],'scene':0,'meshes':[],'skins':[]};b=bytearray()
 for j in [3,4]:
  pos=append(d,b,[[0,0,0],[1,0,0],[0,1,0]],'VEC3');d['accessors'][pos].update(min=[0,0,0],max=[1,1,0])
  joints=append(d,b,[[0,0,0,0]]*3,'VEC4',5123);w=append(d,b,[[1,0,0,0]]*3,'VEC4');bind=append(d,b,[I],'MAT4')
  d['meshes'].append({'primitives':[{'attributes':{'POSITION':pos,'JOINTS_0':joints,'WEIGHTS_0':w}}]});d['skins'].append({'joints':[j],'skeleton':j,'inverseBindMatrices':bind})
 t=append(d,b,[[0],[.15],[.3]],'SCALAR');v=append(d,b,[[0,0,0],[.2,0,0],[0,0,0]],'VEC3')
 d['animations']=[{'name':'Test','samplers':[{'input':t,'output':v}],'channels':[{'sampler':0,'target':{'node':2,'path':'translation'}}]}]
 if detached:
  d['nodes']=[{'name':'Mesh','mesh':0,'skin':0},{'name':'J_Root'},{'name':'J_Head'}];d['scenes']=[{'nodes':[0,1,2]}];d['meshes']=d['meshes'][:1];bind=append(d,b,[I,I],'MAT4');d['skins']=[{'joints':[1,2],'skeleton':1,'inverseBindMatrices':bind}];d['animations'][0]['channels'][0]['target']['node']=0
 d['buffers'][0]['byteLength']=len(b);js=json.dumps(d).encode();js+=b' '*((-len(js))%4);b.extend(b'\0'*((-len(b))%4));path.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(js)+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b)
class SkinUnification(unittest.TestCase):
 def test_pose_geometry_weights_and_connected_skin(self):
  with tempfile.TemporaryDirectory()as tmp:
   source=pathlib.Path(tmp)/'source.glb';out=pathlib.Path(tmp)/'output.glb';fixture(source);original=source.read_bytes();unify(source,out);report=check(source,out)
   self.assertEqual(source.read_bytes(),original);self.assertEqual(report['skins'],1);self.assertEqual(report['joints'],3);self.assertLess(report['max_skin_matrix_error'],1e-5)
 def test_float32_animation_times_remain_strictly_increasing(self):
  with tempfile.TemporaryDirectory()as tmp:
   source=pathlib.Path(tmp)/'source.glb';out=pathlib.Path(tmp)/'output.glb';fixture(source);unify(source,out);d,b=read(out)
   for clip in d['animations']:
    for sampler in clip['samplers']:
     t=[x[0]for x in values(d,b,sampler['input'])];self.assertTrue(all(x<y for x,y in zip(t,t[1:])))
 def test_detached_mesh_motion_moves_skeleton_root(self):
  with tempfile.TemporaryDirectory()as tmp:
   source=pathlib.Path(tmp)/'source.glb';out=pathlib.Path(tmp)/'output.glb';fixture(source,detached=True);unify(source,out);d,b=read(out);root=d['skins'][0]['skeleton'];world=globals_at(d,b,d['animations'][0],.15)
   self.assertAlmostEqual(world[root][3],.2,places=5);self.assertTrue(d['extras']['NARISRepair']['root_motion_migrated_from_detached_mesh']);self.assertLess(check(source,out)['max_skin_matrix_error'],1e-5)
 def test_original_cannot_be_overwritten(self):
  with tempfile.TemporaryDirectory()as tmp:
   source=pathlib.Path(tmp)/'source.glb';fixture(source)
   with self.assertRaises(ValueError):unify(source,source)
 def test_invalid_sampling_rate_is_rejected(self):
  with self.assertRaises(ValueError):unify('missing','output',0)
 def test_rigid_inverse_and_rotation(self):
  m=matrix({'translation':[1,2,3],'rotation':[0,0,2**-.5,2**-.5]})
  self.assertAlmostEqual(m[0],0);self.assertAlmostEqual(m[1],-1)
  for actual,expected in zip(mul(m,inverse(m)),I):self.assertAlmostEqual(actual,expected)
if __name__=='__main__':unittest.main()
