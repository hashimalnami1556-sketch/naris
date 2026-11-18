"""Render actual original and exported weapon/body GLBs in matching CPU views.

This is an offline orthographic texture projection, NEVER an Unreal screenshot.
"""
from pathlib import Path
import argparse, io, json
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from char023_weapon_review import read_glb,audit_source,accessor_array,sha

def base_color_image(doc,blob,pr):
    m=doc['materials'][pr['material']]
    tid=m['pbrMetallicRoughness']['baseColorTexture']['index']
    idx=doc['textures'][tid]['source'];img=doc['images'][idx]
    v=doc['bufferViews'][img['bufferView']];st=v.get('byteOffset',0)
    return Image.open(io.BytesIO(blob[st:st+v['byteLength']])).convert('RGB')

def render(p,faces,colors,axis,w=650,h=790):
    p=np.asarray(p)
    if axis=='front':xx=p[:,0];yy=p[:,1];depth=p[:,2]
    elif axis=='right':xx=-p[:,2];yy=p[:,1];depth=p[:,0]
    else:raise ValueError(axis)
    scale=h*.89;P=np.column_stack((w/2+xx*scale,h*.95-yy*scale))
    im=Image.new('RGB',(w,h),'#22252d');draw=ImageDraw.Draw(im)
    for i in np.argsort(depth[faces].mean(axis=1)):
        draw.polygon([tuple(map(int,v)) for v in P[faces[i]]],fill=tuple(map(int,colors[i])))
    return im

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--candidate-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    doc,blob=read_glb(args.source);pr,f,labels,masks=audit_source(doc,blob,sha(args.source.read_bytes()))
    p=accessor_array(doc,blob,pr['attributes']['POSITION']).astype(float)
    uv=accessor_array(doc,blob,pr['attributes']['TEXCOORD_0'])[f].mean(axis=1)%1
    tex=np.asarray(base_color_image(doc,blob,pr))
    colors=tex[(uv[:,1]*(tex.shape[0]-1)).astype(int),(uv[:,0]*(tex.shape[1]-1)).astype(int)].copy()
    highlight=colors.copy();highlight[masks['blade']]=[0,205,233];highlight[masks['guard']]=[250,173,34]
    bd,bb=read_glb(args.candidate_dir/'NARIS_CHAR023_HeroWithoutWeapon_REVIEW.glb')
    wd,wb=read_glb(args.candidate_dir/'NARIS_CHAR023_RigidWeaponCandidate_REVIEW.glb')
    bpr=bd['meshes'][0]['primitives'][0]
    bp=accessor_array(bd,bb,bpr['attributes']['POSITION']).astype(float)
    bf=accessor_array(bd,bb,bpr['indices']).astype(int).reshape(-1,3)
    buv=accessor_array(bd,bb,bpr['attributes']['TEXCOORD_0'])[bf].mean(axis=1)%1
    bcolors=tex[(buv[:,1]*(tex.shape[0]-1)).astype(int),(buv[:,0]*(tex.shape[1]-1)).astype(int)]
    wprs=wd['meshes'][0]['primitives'];wattr=wprs[0]['attributes']
    wp=accessor_array(wd,wb,wattr['POSITION']).astype(float)+np.asarray(wd['nodes'][0]['translation'])
    wuv=accessor_array(wd,wb,wattr['TEXCOORD_0'])
    assembled_p=np.vstack((bp,wp));assembled_f=np.empty((len(f),3),dtype=int);assembled_c=np.empty_like(colors)
    assembled_f[masks['body']]=bf;assembled_c[masks['body']]=bcolors
    for name,part in zip(('guard','blade'),wprs):
        sf=accessor_array(wd,wb,part['indices']).astype(int).reshape(-1,3)
        assembled_f[masks[name]]=sf+len(bp)
        tuv=wuv[sf].mean(axis=1)%1
        assembled_c[masks[name]]=tex[(tuv[:,1]*(tex.shape[0]-1)).astype(int),(tuv[:,0]*(tex.shape[1]-1)).astype(int)]
    delta=float(np.max(np.abs(p[f]-assembled_p[assembled_f])))
    if delta>6e-8 or not np.array_equal(colors,assembled_c):
        raise AssertionError('Actual output GLB reconstruction altered source appearance')
    width,height,gap,head,foot=650,790,16,110,58
    sheet=Image.new('RGB',(3*width+4*gap,2*(height+78)+head+foot),'#181c23')
    draw=ImageDraw.Draw(sheet)
    draw.text((gap,22),'CALL OF NARIS | CHAR-023 | SOURCE GEOMETRY AUDIT',fill='#f1f4f6')
    draw.text((gap,48),'CPU view from original and TWO exported GLBs. Not an Unreal screenshot.',fill='#aab4c7')
    differences=0
    for row,axis in enumerate(('front','right')):
        before=render(p,f,colors,axis,width,height)
        review=render(p,f,highlight,axis,width,height)
        after=render(assembled_p,assembled_f,assembled_c,axis,width,height)
        diff=ImageChops.difference(before,after)
        if diff.getbbox():differences+=sum(1 for v in diff.getdata() if any(v))
        for col,(im,label) in enumerate(zip((before,review,after),('BEFORE: ORIGINAL','REVIEW: BLADE / GUARD','AFTER: EXPORTED GLB REASSEMBLED'))):
            x=gap+col*(width+gap);y=head+row*(height+78)
            sheet.paste(im,(x,y+32));draw.text((x,y+8),f'{axis.upper()} | {label}',fill='#f3f3f3')
    draw.text((gap,sheet.height-foot+14),f'Actual reassembly {differences} differing pixels; max source-unit coord delta {delta:.2g}. REVIEW ONLY.',fill='#a9c4d9')
    if args.out.exists():raise ValueError('Refusing to overwrite prior screenshot')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(args.out)
    print(json.dumps({'pixel_differences':differences,'max_world_coordinate_difference_source_units':delta,'views':['front','right'],'scope':'CPU geometry only'}))

if __name__=='__main__':main()
