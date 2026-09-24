"""Deterministic source blockouts. No DCC/engine approval is implied."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ('FLOOR','WALL','ARCH','PILLAR','STAIRS','BRIDGE','FENCE','ALTAR','OBELISK','CRYSTAL','STUMP','TREE','RUBBLE','BENCH','BRAZIER','PLINTH','TOWER','BARRICADE','GATE','WELL')
PACK = 'assets/w04-expansion'

class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []
    def box(self, x, y, z, w, d, h):
        n = len(self.vertices)
        self.vertices += [(x+sx*w/2,y+sy*d/2,z+sz*h/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.faces += [tuple(n+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
    def cone(self,x,y,z,r0,r1,h,sides=8):
        n=len(self.vertices)
        for r,dz in [(r0,0),(r1,h)]:
            self.vertices += [(x+r*math.cos(i*math.tau/sides),y+r*math.sin(i*math.tau/sides),z+dz) for i in range(sides)]
        self.faces.append(tuple(n+i for i in reversed(range(sides))))
        self.faces.append(tuple(n+sides+i for i in range(sides)))
        self.faces += [(n+i,n+(i+1)%sides,n+sides+(i+1)%sides,n+sides+i) for i in range(sides)]
    def data(self):
        return {'vertices':[[round(v,6) for v in p] for p in self.vertices], 'faces':self.faces}

def build(family, variant):
    m=Mesh(); v=variant; h=2+0.35*v; w=2+0.4*v
    if family=='FLOOR':
        for i in range(v+1): m.box(0,(i-v/2)*0.8,0.1,4,0.78,0.2)
    elif family=='WALL':
        for row in range(v+2):
            for col in range(4):m.box((col-1.5)*1.0+(row%2)*0.15,0,0.25+row*0.5,0.98,0.4,0.48)
    elif family in ('ARCH','GATE'):
        for x in (-w/2,w/2): m.box(x,0,h/2,0.4,0.6,h)
        if family=='ARCH':
            for i in range(9):
                a=i*math.pi/8;m.box(math.cos(a)*w/2,0,h+math.sin(a)*w/2,0.4,0.6,0.4)
        else:
            m.box(0,0,h, w+0.4,0.6,0.4)
            for i in range(v+3):m.box((i-(v+2)/2)*w/(v+3),0,h/2,0.1,0.1,h)
    elif family in ('PILLAR','OBELISK','CRYSTAL','STUMP','PLINTH'):
        r=0.3+0.07*v
        if family=='CRYSTAL':m.cone(0,0,0,r,r*0.8,h*.7,5+v);m.cone(0,0,h*.7,r*.8,.015,h*.3,5+v)
        elif family=='STUMP':m.cone(0,0,0,r*1.8,r,0.4+v*.15,7+v)
        elif family=='PLINTH':m.box(0,0,.15,w,w,.3);m.box(0,0,.5,w*.7,w*.7,.4)
        else:
            m.box(0,0,.15,1.2,1.2,.3);m.cone(0,0,.3,r,r if family=='PILLAR' else .06,h,8+v)
            if family=='PILLAR':m.box(0,0,h+.4,1.2,1.2,.2)
    elif family=='STAIRS':
        for i in range(v+3):m.box(0,i*.4,(i+1)*.1,w,.4,(i+1)*.2)
    elif family=='BRIDGE':
        for i in range(v+5):m.box(0,i*.5,.7,2.4,.48,.2)
        for x in (-1,1):m.box(x,(v+4)*.25,.35,.2,(v+5)*.5,.7)
    elif family in ('FENCE','BARRICADE'):
        for i in range(v+3):m.box((i-(v+2)/2)*.6,0,.7,.18,.2,1.4+(i%2)*.25)
        for z in (.4,1.0):m.box(0,0,z,(v+3)*.6,.22,.15)
        if family=='BARRICADE':
            for x in (-.7,.7):m.box(x,0,.1,.2,1.4,.2)
    elif family in ('ALTAR','BENCH'):
        for x in (-w*.35,w*.35):m.box(x,0,.4,.3,.7,.8)
        m.box(0,0,.9,w,1 if family=='ALTAR' else .6,.2)
        if family=='ALTAR':m.cone(0,0,1,.3,.1,.35,6+v)
    elif family=='TREE':
        m.cone(0,0,0,.35,.1,h+1,8)
        for i in range(v+2):
            z=1+i*.4; sign=(-1)**i;m.box(sign*.5,0,z,1,.12,.15);m.cone(sign*.9,0,z,.1,.03,.6,6)
    elif family=='RUBBLE':
        for i in range(v+4):
            a=i*2.399;m.cone(math.cos(a)*.7,math.sin(a)*.7,0,.2+(i%3)*.08,.12,.2+(i%2)*.2,5+i%3)
    elif family=='BRAZIER':
        m.cone(0,0,0,.4,.18,.7,8+v);m.cone(0,0,.7,.18,.5,.3,8+v)
        for i in range(v+4):
            a=i*math.tau/(v+4);m.box(.5*math.cos(a),.5*math.sin(a),1.12,.08,.08,.25)
    elif family=='TOWER':
        m.cone(0,0,0,w/2,w/2,h,8+v)
        for i in range(v+4):
            a=i*math.tau/(v+4);m.box(w/2*math.cos(a),w/2*math.sin(a),h+.2,.35,.35,.4)
    elif family=='WELL':
        for i in range(12):
            a=i*math.tau/12;m.box(math.cos(a)*w/2,math.sin(a)*w/2,.4,.4,.4,.8)
    else:raise ValueError(family)
    return m

def generate(root=ROOT):
    registry_path=root/'data/MASTER_ASSET_REGISTRY.json'; registry=json.loads(registry_path.read_text())
    pack=root/PACK;pack.mkdir(parents=True,exist_ok=True); entries=[]; additions=[]
    for index in range(97):
        family=FAMILIES[index//5];variant=index%5+1; asset_id=f'NARIS-W04-ENV-{family}-{1000+variant:04d}'
        mesh=build(family,variant); data=mesh.data();raw=json.dumps(data,separators=(',',':'))+'\n'
        path=pack/f'{asset_id}.mesh.json';path.write_text(raw)
        obj='# NARIS procedural blockout; meters; Z up\no '+asset_id+'\n'
        obj+=''.join('v '+' '.join(map(str,p))+'\n' for p in data['vertices'])
        obj+=''.join('f '+' '.join(str(i+1) for i in f)+'\n' for f in data['faces'])
        (pack/f'{asset_id}.obj').write_text(obj)
        entries.append({'id':asset_id,'family':family,'variant':variant,'mesh':str(path.relative_to(root)),'sha256':hashlib.sha256(raw.encode()).hexdigest(),'vertices':len(mesh.vertices),'triangles':sum(len(f)-2 for f in mesh.faces)})
        additions.append({'id':asset_id,'name':f'Ashen {family.title()} {variant}','domain':'ENV','type':family,'world':'W04','status':'blockout','source':str(path.relative_to(root)),'engine_target':'Unreal','notes':'Procedural source geometry; UV generation at Blender intake. Engine/collision/LOD/material QA pending.'})
    existing={a['id']:a for a in registry['assets']}
    for a in additions:
        if a['id'] in existing and existing[a['id']] != a:raise ValueError('Refusing to overwrite existing registry identity '+a['id'])
    registry['assets'] += [a for a in additions if a['id'] not in existing]
    registry_path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
    (pack/'manifest.json').write_text(json.dumps({'schema':'naris.source.blockout.v1','units':'meters','up_axis':'Z','status':'blockout','assets':entries},indent=2)+'\n')
    return entries

if __name__=='__main__':print(f'Generated {len(generate())} source blockouts')
