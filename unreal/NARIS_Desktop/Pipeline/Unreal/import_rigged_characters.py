import unreal, os, traceback
ROOT="/Game/Art/Characters/Rigged"
SRC=r"C:\Users\Admin\NARIS\Pipeline\Exchange\FBX\Rigged"

chars=[
 ("AshenVessel","SK_AshenVessel.fbx",["AN_Ashen_Attack","AN_Ashen_Idle","AN_Ashen_Walk"]),
 ("CelestialWolf","SK_CelestialWolf.fbx",["AN_Wolf_Bite","AN_Wolf_Idle","AN_Wolf_Run"]),
 ("BoneBeast","SK_BoneBeast.fbx",["AN_Beast_Idle","AN_Beast_Run","AN_Beast_Swipe"])
]

if unreal.EditorAssetLibrary.does_directory_exist(ROOT):
    unreal.EditorAssetLibrary.delete_directory(ROOT)
unreal.EditorAssetLibrary.make_directory(ROOT)

asset_tools=unreal.AssetToolsHelpers.get_asset_tools()
results={}

for cname,fbx,anim_names in chars:
    dest=ROOT+"/"+cname
    unreal.EditorAssetLibrary.make_directory(dest)
    ui=unreal.FbxImportUI()
    ui.import_mesh=True
    ui.import_as_skeletal=True
    ui.import_animations=True
    ui.import_materials=False
    ui.import_textures=False
    ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
    try:
        ui.skeleton=None
    except Exception:
        pass

    task=unreal.AssetImportTask()
    task.filename=os.path.join(SRC,fbx)
    task.destination_path=dest
    task.automated=True
    task.replace_existing=True
    task.save=True
    task.options=ui
    asset_tools.import_asset_tasks([task])

    imported=[str(x) for x in task.imported_object_paths]
    unreal.log("NARIS_RIG_REIMPORT "+cname+" "+",".join(imported))

    assets=unreal.EditorAssetLibrary.list_assets(dest,recursive=False,include_folder=False)
    for target in anim_names:
        for path in list(assets):
            if target in path and not path.endswith("/"+target+"."+target):
                old=path.split(".")[0]
                new=dest+"/"+target
                if unreal.EditorAssetLibrary.does_asset_exist(old):
                    unreal.EditorAssetLibrary.rename_asset(old,new)
                    break

    meshes=[]
    skeletons=[]
    for path in unreal.EditorAssetLibrary.list_assets(dest,recursive=False,include_folder=False):
        obj=unreal.load_asset(path)
        if isinstance(obj,unreal.SkeletalMesh):
            sk=obj.get_editor_property("skeleton")
            meshes.append((path,str(sk.get_path_name()) if sk else "NONE"))
        if isinstance(obj,unreal.Skeleton):
            skeletons.append(path)
    results[cname]={"meshes":meshes,"skeleton_assets":skeletons}
    unreal.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False,recursive=True)

unreal.log("NARIS_RIG_REIMPORT_RESULTS "+str(results))
skels=[v["meshes"][0][1] for v in results.values() if v["meshes"]]
if len(skels)==3 and len(set(skels))==3:
    unreal.log("NARIS_RIG_SKELETON_CHECK PASS "+str(skels))
else:
    unreal.log_error("NARIS_RIG_SKELETON_CHECK FAIL "+str(skels))
