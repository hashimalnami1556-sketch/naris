"""Numerical bind/pose checks. Does not evaluate organic deformation or Unreal."""
import argparse,json,pathlib
from unify_skin import read,values,globals_at,mul,I

def check(source,repaired):
 a,ab=read(source);d,db=read(repaired);skin=d['skins'][0];root=skin['skeleton'];joints=skin['joints'][1:];matrices=values(d,db,skin['inverseBindMatrices']);matrices=[[m[c*4+r]for r in range(4)for c in range(4)]for m in matrices]
 assert len(d['skins'])==1
 parents={c:i for i,n in enumerate(d['nodes'])for c in n.get('children',[])}
 for j in joints:
  seen=set();n=j
  while n!=root:
   assert n not in seen and n in parents,'Disconnected or cyclic skeleton';seen.add(n);n=parents[n]
 original_matrices={}
 for s in a['skins']:
  for j,m in zip(s['joints'],values(a,ab,s['inverseBindMatrices'])):original_matrices[j]=[m[c*4+r]for r in range(4)for c in range(4)]
 assert a.get('images')==d.get('images') and a.get('materials')==d.get('materials')
 vertices=0
 for am,dm in zip(a['meshes'],d['meshes']):
  for ap,dp in zip(am['primitives'],dm['primitives']):
   for attr,acc in ap['attributes'].items():
    if attr!='JOINTS_0':assert values(a,ab,acc)==values(d,db,dp['attributes'][attr]),'Geometry/weights changed'
   w=values(d,db,dp['attributes']['WEIGHTS_0']);js=values(d,db,dp['attributes']['JOINTS_0']);vertices+=len(w)
   assert all(abs(sum(row)-1)<1e-5 and min(row)>=0 for row in w)
   assert all(0<=j<len(skin['joints'])for row in js for j in row)
 names=[c.get('name')for c in a.get('animations',[])];assert names==[c.get('name')for c in d.get('animations',[])]
 metadata=d['extras']['NARISRepair'];max_error=0.;samples=0;root_motion=[]
 for ac,dc in zip(a.get('animations',[]),d.get('animations',[])):
  keys=sorted(set(t[0]for s in ac['samplers']for t in values(a,ab,s['input'])));end=keys[-1]
  times=sorted(set(keys+[end*i/20 for i in range(21)]))
  for t in times:
   aw=globals_at(a,ab,ac,t);dw=globals_at(d,db,dc,t)
   for k,j in enumerate(joints):
    expected=mul(aw[j],original_matrices[j])
    if metadata['root_motion_migrated_from_detached_mesh']:expected=mul(aw[metadata['root_driver_node']],expected)
    actual=mul(dw[j],matrices[k+1]);max_error=max(max_error,max(abs(x-y)for x,y in zip(expected,actual)));samples+=1
  first=globals_at(d,db,dc,0)[root];last=globals_at(d,db,dc,end)[root];distance=sum((last[k]-first[k])**2 for k in [3,7,11])**.5
  if dc.get('name','').startswith('P15_'):root_motion.append({'clip':dc['name'],'root_displacement':distance})
 assert max_error<.002,('Pose error exceeds tolerance',max_error)
 return {'source':pathlib.Path(source).name,'output':pathlib.Path(repaired).name,'skins':1,'joints':len(skin['joints']),'clips':len(names),'vertices':vertices,'matrix_comparisons':samples,'max_skin_matrix_error':max_error,'root_motion':root_motion,'geometry_and_weights_unchanged':True,'connected':True,'scope':'CPU numerical comparison; not visual or Unreal acceptance'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('repaired');a=p.parse_args();print(json.dumps(check(a.source,a.repaired),indent=2))
