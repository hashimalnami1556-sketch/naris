"""Bind discovered PBR textures to W04 material instances.
Only exact canonical suffixes are accepted; no placeholder textures are created.
"""
import unreal, json
from pathlib import Path

ROOT="/Game/NARIS/W04"
SUFFIX={"BaseColor":"_BC","Normal":"_N","Roughness":"_R","Metallic":"_M","AO":"_AO","Height":"_H"}
errors=[]; bound=[]
assets=unreal.EditorAssetLibrary.list_assets(ROOT,recursive=True,include_folder=False)
textures={}
for p in assets:
    obj=unreal.load_asset(p)
    if isinstance(obj,unreal.Texture):
        textures[p.rsplit("/",1)[-1].split(".",1)[0]]=obj

instances=[p for p in assets if "/Materials/MI_" in p]
for p in instances:
    mi=unreal.load_asset(p)
    if not isinstance(mi,unreal.MaterialInstanceConstant): continue
    stem=p.rsplit("/",1)[-1].split(".",1)[0].replace("MI_","T_")
    for param,sfx in SUFFIX.items():
        candidates=[v for k,v in textures.items() if k==stem+sfx]
        if not candidates: continue
        ok=unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi,unreal.Name(param),candidates[0])
        if ok: bound.append(p+":"+param)
        else: errors.append(p+":parent_missing_texture_parameter:"+param)
    unreal.MaterialEditingLibrary.update_material_instance(mi)
unreal.EditorAssetLibrary.save_directory(ROOT+"/Materials",only_if_is_dirty=False,recursive=True)
report={"schema":"naris.stage33.pbr-texture-bind.v1","bound_count":len(bound),"bound":bound,"errors":errors}
out=Path(unreal.Paths.project_saved_dir())/"TestReports"; out.mkdir(parents=True,exist_ok=True)
(out/"naris_stage33_pbr_texture_bind.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
unreal.log("NARIS_STAGE33_PBR_BIND="+json.dumps(report))
if errors: raise RuntimeError("Stage33 PBR texture binding errors")
