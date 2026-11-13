"""CHAR-022 cape review: non-destructive partition of the repaired prototype.
Not production garment segmentation or cloth. Uses source UV colors and posterior geometry.
"""
import argparse, copy, hashlib, io, json
from pathlib import Path
import numpy as np
from PIL import Image
from char022_repair_skin import read_glb, array, write_glb

SOURCE_SHA="a9389d433d31886c1d4273e6acda0950ca6657fac20338063b9bb643ca95fdd9"

def partition(doc, blob):
    if (len(doc["meshes"])!=1 or len(doc["meshes"][0]["primitives"])!=1
        or doc["nodes"][18].get("skin")!=0 or len(doc["skins"][0]["joints"])!=18):
        raise ValueError("Expected exact CHAR-022 repaired prototype")
    original=doc["meshes"][0]["primitives"][0]
    if original["indices"]!=3 or original["attributes"]["POSITION"]!=0 or original["attributes"]["TEXCOORD_0"]!=2:
        raise ValueError("Unexpected accessor layout")
    pos=array(doc,blob,0);tri=array(doc,blob,3).reshape(-1,3);uv=array(doc,blob,2)
    if len(pos)!=32373 or len(tri)!=49886:
        raise ValueError("Unexpected topology")
    material=doc["materials"][original["material"]]
    texid=material["pbrMetallicRoughness"]["baseColorTexture"]["index"]
    image=doc["images"][doc["textures"][texid]["source"]]
    view=doc["bufferViews"][image["bufferView"]];start=view.get("byteOffset",0)
    tex=np.asarray(Image.open(io.BytesIO(blob[start:start+view["byteLength"]])).convert("RGB"))
    coords=uv[tri].mean(axis=1)%1
    rgb=tex[(coords[:,1]*(tex.shape[0]-1)).astype(int),(coords[:,0]*(tex.shape[1]-1)).astype(int)].astype(float)
    r,g,b=rgb.T
    verts=pos[tri]
    # Conservative posterior burgundy fabric mask; collar, front cloth and
    # uncertain/dark boundaries intentionally remain in Body review section.
    mask=(r>1.5*g+5)&(r>1.4*b+5)&(r>27)&(b>=g-2)&(verts[:,:,2].max(1)<-.065)&(verts[:,:,1].min(1)>.14)&(verts[:,:,1].max(1)<.82)
    ids=np.flatnonzero(mask)
    if not len(ids) or mask.all(): raise ValueError("Empty partition")
    d=copy.deepcopy(doc);data=bytearray(blob);sections=[]
    for name,selected in (("Body_Review",~mask),("Cape_Candidate_Review",mask)):
        idx=tri[selected].astype("<u2").reshape(-1)
        data.extend(b"\0"*((-len(data))%4));offset=len(data)
        data.extend(idx.tobytes())
        view_index=len(d["bufferViews"])
        d["bufferViews"].append({"buffer":0,"byteOffset":offset,"byteLength":idx.nbytes,"target":34963})
        accessor=len(d["accessors"])
        d["accessors"].append({"bufferView":view_index,"componentType":5123,"count":len(idx),"type":"SCALAR","min":[int(idx.min())],"max":[int(idx.max())]})
        prim=copy.deepcopy(original);prim["indices"]=accessor
        prim["extras"]={"naris_section":name,"review_only":True}
        sections.append(prim)
    data.extend(b"\0"*((-len(data))%4))
    d["buffers"][0]["byteLength"]=len(data)
    d["meshes"][0]["primitives"]=sections
    body=np.unique(tri[~mask]);cape=np.unique(tri[mask])
    shared=np.intersect1d(body,cape)
    report={"id":"CHAR-022-CAPE","selection_status":"REVIEW_REQUIRED","original_triangles":len(tri),
        "body_triangles":int((~mask).sum()),"candidate_triangles":int(mask.sum()),"original_vertices":len(pos),
        "body_referenced_vertices":len(body),"cape_referenced_vertices":len(cape),"shared_boundary_vertices":len(shared),
        "original_joints":18,"new_bones":0,"original_binary_prefix_preserved":bytes(data[:len(blob)])==blob,
        "cloth_simulation":"NOT_RUN","leg_collision":"NOT_RUN","ue_import":"NOT_RUN","production_approved":False,
        "limitations":"Color/geometry mask is heuristic; connected source mesh and shared boundary require artist review before physics. No separate garment or cloth weights created."}
    return d,bytes(data),ids,report

def main():
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("output",type=Path)
    p.add_argument("--report",type=Path,required=True);p.add_argument("--face-ids",type=Path,required=True)
    args=p.parse_args()
    paths=[x.resolve() for x in (args.source,args.output,args.report,args.face_ids)]
    if len(set(paths))!=4 or any(x.exists() for x in paths[1:]):raise SystemExit("Refusing overwrite")
    if hashlib.sha256(args.source.read_bytes()).hexdigest()!=SOURCE_SHA:raise SystemExit("Source SHA mismatch")
    doc,blob=read_glb(args.source);d,b,ids,report=partition(doc,blob)
    write_glb(args.output,d,b)
    args.face_ids.write_text(json.dumps(ids.tolist(),separators=(",",":"))+"\n")
    report["source_sha256"]=SOURCE_SHA;report["output_sha256"]=hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2))
if __name__=="__main__": main()
