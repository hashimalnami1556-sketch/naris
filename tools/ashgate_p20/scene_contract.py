"""Read-only GLB scene graph checks for NARIS Ash Gate."""
import json, pathlib, struct
from stage_gate import verify_stage, LAYERS

def validate_gltf_graph(g):
    errors=[]
    nodes=g.get("nodes",[]); meshes=g.get("meshes",[]); scenes=g.get("scenes",[])
    if not scenes: errors.append("no scenes")
    if not meshes: errors.append("no meshes")
    if not nodes: errors.append("no nodes")
    default=g.get("scene",0)
    if not isinstance(default,int) or default<0 or default>=len(scenes):
        errors.append("default scene out of range")
    for i,scene in enumerate(scenes):
        for n in scene.get("nodes",[]):
            if not isinstance(n,int) or n<0 or n>=len(nodes):
                errors.append(f"scene {i}: bad node")
    for i,node in enumerate(nodes):
        m=node.get("mesh")
        if m is not None and (not isinstance(m,int) or m<0 or m>=len(meshes)):
            errors.append(f"node {i}: invalid mesh")
        for child in node.get("children",[]):
            if not isinstance(child,int) or child<0 or child>=len(nodes):
                errors.append(f"node {i}: invalid child")
    for i,mesh in enumerate(meshes):
        if not mesh.get("primitives"): errors.append(f"mesh {i}: no primitives")
    return errors

def inspect_scene(path):
    data=pathlib.Path(path).read_bytes()
    if len(data)<20 or data[:4]!=b"glTF":
        return {"meshes":0,"nodes":0,"scenes":0,"errors":["not GLB"]}
    length,typ=struct.unpack_from("<I4s",data,12)
    if typ!=b"JSON" or 20+length>len(data):
        return {"meshes":0,"nodes":0,"scenes":0,"errors":["invalid JSON chunk"]}
    try: g=json.loads(data[20:20+length])
    except (ValueError,UnicodeDecodeError):
        return {"meshes":0,"nodes":0,"scenes":0,"errors":["unreadable JSON chunk"]}
    return {"meshes":len(g.get("meshes",[])),"nodes":len(g.get("nodes",[])),
            "scenes":len(g.get("scenes",[])),"errors":validate_gltf_graph(g)}

def validate_scene_contract(asset_dir):
    root=pathlib.Path(asset_dir)
    gate=verify_stage(root)
    errors=list(gate["errors"]); layers={}
    for name in LAYERS:
        path=root/(name+".glb")
        if not path.exists(): continue
        report=inspect_scene(path); layers[name]=report
        errors.extend(name+": "+e for e in report["errors"])
    return {"ok":not errors,"errors":errors,"layers":layers,"runtime_verified":False}
