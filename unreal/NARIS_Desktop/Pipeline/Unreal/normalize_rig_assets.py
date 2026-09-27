import unreal
DEST="/Game/Art/Characters/Rigged"
assets=unreal.EditorAssetLibrary.list_assets(DEST,recursive=False,include_folder=False)
for p in assets:
    d=unreal.EditorAssetLibrary.find_asset_data(p)
    cls=str(d.asset_class_path.asset_name)
    obj=unreal.load_asset(p)
    extra=""
    try:
        if isinstance(obj,unreal.SkeletalMesh):
            extra=" skeleton="+str(obj.get_editor_property("skeleton"))
        elif isinstance(obj,unreal.AnimSequence):
            extra=" skeleton="+str(obj.get_editor_property("skeleton"))
    except Exception as e:
        extra=" inspect_error="+str(e)
    unreal.log("NARIS_ASSET_INSPECT "+p+" class="+cls+extra)

renames={
"/Game/Art/Characters/Rigged/SK_AshenVesselSK_AshenVessel_Armature_AN_Ashen_Attack":"/Game/Art/Characters/Rigged/AN_Ashen_Attack",
"/Game/Art/Characters/Rigged/SK_AshenVesselSK_AshenVessel_Armature_AN_Ashen_Idle":"/Game/Art/Characters/Rigged/AN_Ashen_Idle",
"/Game/Art/Characters/Rigged/SK_AshenVesselSK_AshenVessel_Armature_AN_Ashen_Walk":"/Game/Art/Characters/Rigged/AN_Ashen_Walk",
"/Game/Art/Characters/Rigged/SK_CelestialWolfSK_CelestialWolf_Armature_AN_Wolf_Bite":"/Game/Art/Characters/Rigged/AN_Wolf_Bite",
"/Game/Art/Characters/Rigged/SK_CelestialWolfSK_CelestialWolf_Armature_AN_Wolf_Idle":"/Game/Art/Characters/Rigged/AN_Wolf_Idle",
"/Game/Art/Characters/Rigged/SK_CelestialWolfSK_CelestialWolf_Armature_AN_Wolf_Run":"/Game/Art/Characters/Rigged/AN_Wolf_Run",
"/Game/Art/Characters/Rigged/SK_BoneBeastSK_BoneBeast_Armature_AN_Beast_Idle":"/Game/Art/Characters/Rigged/AN_Beast_Idle",
"/Game/Art/Characters/Rigged/SK_BoneBeastSK_BoneBeast_Armature_AN_Beast_Run":"/Game/Art/Characters/Rigged/AN_Beast_Run",
"/Game/Art/Characters/Rigged/SK_BoneBeastSK_BoneBeast_Armature_AN_Beast_Swipe":"/Game/Art/Characters/Rigged/AN_Beast_Swipe"
}
for old,new in renames.items():
    if unreal.EditorAssetLibrary.does_asset_exist(old):
        ok=unreal.EditorAssetLibrary.rename_asset(old,new)
        unreal.log("NARIS_RENAME "+old+" -> "+new+" "+str(ok))
unreal.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=False,recursive=True)
unreal.log("NARIS_RIG_NORMALIZE_DONE")
