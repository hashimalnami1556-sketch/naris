import unreal, os, json, traceback
DEST_ROOT="/Game/Art/Characters/RiggedV4"
SRC=r"C:\Users\Admin\NARIS\Pipeline\Exchange\FBX\RiggedV4"
REPORT=r"C:\Users\Admin\NARIS\Pipeline\Unreal\RIG_IMPORT_REPORT_V4.json"
CHARS={
 "AshenVessel":("SK_AshenVessel.fbx",["AN_Ashen_Attack_Heavy","AN_Ashen_Attack_Light","AN_Ashen_Dodge","AN_Ashen_HitReact","AN_Ashen_Idle","AN_Ashen_Walk","AN_Ashen_Run","AN_Ashen_Parry","AN_Ashen_Resonance"]),
 "CelestialWolf":("SK_CelestialWolf.fbx",["AN_Wolf_Bite","AN_Wolf_Dash","AN_Wolf_Idle","AN_Wolf_Roar","AN_Wolf_Run","AN_Wolf_SoulVision"]),
 "BoneBeast":("SK_BoneBeast.fbx",["AN_Beast_Idle","AN_Beast_Roar","AN_Beast_Run","AN_Beast_Stunned","AN_Beast_Swipe","AN_Beast_TailSweep","AN_Beast_Enrage"])
}
tools=unreal.AssetToolsHelpers.get_asset_tools()
if not unreal.EditorAssetLibrary.does_directory_exist(DEST_ROOT):
 unreal.EditorAssetLibrary.make_directory(DEST_ROOT)
report={"version":4,"characters":{},"errors":[]}

for cname,(filename,expected_anims) in CHARS.items():
 dest=DEST_ROOT+"/"+cname
 unreal.EditorAssetLibrary.make_directory(dest)
 ui=unreal.FbxImportUI()
 ui.import_mesh=True; ui.import_as_skeletal=True; ui.import_animations=True
 ui.import_materials=False; ui.import_textures=False
 ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
 ui.automated_import_should_detect_type=False
 try:
  ui.skeletal_mesh_import_data.import_mesh_lods=False
 except Exception as e:
  unreal.log_warning("NARIS_V2_IMPORT_OPTION "+str(e))
 task=unreal.AssetImportTask()
 task.filename=os.path.join(SRC,filename); task.destination_path=dest
 task.automated=True; task.replace_existing=True; task.save=True; task.options=ui
 try:
  tools.import_asset_tasks([task])
  raw=[str(x) for x in task.imported_object_paths]
  assets=unreal.EditorAssetLibrary.list_assets(dest,recursive=False,include_folder=False)
  for target in expected_anims:
   exact=dest+"/"+target
   if unreal.EditorAssetLibrary.does_asset_exist(exact): continue
   candidates=sorted([p for p in assets if target.lower() in p.lower()],key=lambda p:(0 if ("Armature_"+target).lower() in p.lower() else 1,len(p)))
   if candidates:
    old=candidates[0].split(".")[0]
    if old!=exact: unreal.EditorAssetLibrary.rename_asset(old,exact)
    assets=unreal.EditorAssetLibrary.list_assets(dest,recursive=False,include_folder=False)
  meshes=[]; skels=[]; anims=[]
  for p in unreal.EditorAssetLibrary.list_assets(dest,recursive=False,include_folder=False):
   obj=unreal.load_asset(p)
   if isinstance(obj,unreal.SkeletalMesh):
    sk=obj.get_editor_property("skeleton")
    meshes.append({"asset":p,"skeleton":sk.get_path_name() if sk else None})
   elif isinstance(obj,unreal.Skeleton): skels.append(p)
   elif isinstance(obj,unreal.AnimSequence): anims.append(p)
  missing=[a for a in expected_anims if not unreal.EditorAssetLibrary.does_asset_exist(dest+"/"+a)]
  report["characters"][cname]={"raw_imports":raw,"meshes":meshes,"skeletons":skels,"animations":sorted(anims),"missing_expected":missing}
  if missing: report["errors"].append(cname+" missing animations: "+",".join(missing))
  if len(meshes)!=1: report["errors"].append(cname+" mesh_count="+str(len(meshes)))
  unreal.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False,recursive=True)
 except Exception:
  err=traceback.format_exc(); report["errors"].append(cname+" import exception")
  report["characters"][cname]={"exception":err}; unreal.log_error(err)

with open(REPORT,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
if report["errors"]:
 unreal.log_error("NARIS_RIG_V4_IMPORT_FAIL "+str(report["errors"]))
else:
 unreal.log("NARIS_RIG_V4_IMPORT_PASS")
unreal.log("NARIS_RIG_V4_IMPORT_REPORT "+REPORT)

