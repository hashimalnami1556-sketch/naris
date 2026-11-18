"""ANIM-024: fail-closed source GLB animation coverage; no fake runtime certification."""
import argparse,hashlib,json,struct
from pathlib import Path
REQUIRED=('idle','walk','run','attack','dodge','block','death')
def gate(coverage):
    missing=[k for k in REQUIRED if not coverage.get(k,False)]
    return {'minimum_named_clip_coverage':not missing,'production_ready':False,'missing':missing,
            'required':list(REQUIRED),'reason':'UE runtime, bone coverage and retarget tests required'}
def inspect_gltf(doc):
    nodes=doc.get('nodes',[]);clips=[]
    for anim in doc.get('animations',[]):
        targets=[];paths=[]
        for c in anim.get('channels',[]):
            t=c.get('target',{});idx=t.get('node')
            if not isinstance(idx,int) or idx<0 or idx>=len(nodes):
                raise ValueError('Animation target out of bounds')
            targets.append(nodes[idx].get('name',str(idx)));paths.append(t.get('path'))
        clips.append({'name':anim.get('name',''),'channels':len(anim.get('channels',[])),
                      'animated_nodes':sorted(set(targets)),'paths':sorted(set(paths))})
    coverage={k:any(c['name'].casefold().startswith(k) or ('_'+k) in c['name'].casefold()
                     for c in clips) for k in REQUIRED}
    return {'clip_count':len(clips),'clips':clips,'named_clip_coverage':coverage,
            'gate':gate(coverage),'runtime_verified':False}
def inspect_file(path):
    data=Path(path).read_bytes()
    if len(data)<20 or struct.unpack_from('<4sII',data,0)!=(b'glTF',2,len(data)):
        raise ValueError('Invalid GLB header')
    n,tag=struct.unpack_from('<I4s',data,12)
    if tag!=b'JSON' or 20+n>len(data):raise ValueError('Invalid JSON chunk')
    d=json.loads(data[20:20+n]);r=inspect_gltf(d)
    r.update({'source':Path(path).name,'sha256':hashlib.sha256(data).hexdigest(),
              'skin_count':len(d.get('skins',[])),'node_count':len(d.get('nodes',[]))})
    return r
def main():
    p=argparse.ArgumentParser();p.add_argument('files',nargs='+',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise SystemExit('Refusing to overwrite evidence')
    result={'id':'ANIM-024','status':'SOURCE_COVERAGE_ONLY',
            'assets':[inspect_file(f) for f in a.files],
            'engine_tests':'NOT_RUN','retargeter':'NOT_CREATED','combat_montages':'NOT_CREATED',
            'rollback':'Audit only; no asset modification'}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'files':len(result['assets']),
          'blocked':[x['source'] for x in result['assets'] if not x['gate']['minimum_named_clip_coverage']]}))
if __name__=='__main__':main()
