import unreal
MAP_DIR="/Game/World/Maps"
MAP_PATH=MAP_DIR+"/L_AshenForest_VerticalSlice"
unreal.EditorAssetLibrary.make_directory(MAP_DIR)
if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
    unreal.EditorAssetLibrary.delete_asset(MAP_PATH)
unreal.EditorLevelLibrary.new_level(MAP_PATH)

for path,loc in [
("/Game/Art/Imported/ENV_AshenGround.ENV_AshenGround",(0,0,0)),
("/Game/Art/Imported/ENV_GatePillar.ENV_GatePillar",(-350,900,250)),
("/Game/Art/Imported/ENV_GatePillar_001.ENV_GatePillar_001",(350,900,250)),
("/Game/Art/Imported/ENV_GateLintel.ENV_GateLintel",(0,900,500))]:
    obj=unreal.load_asset(path)
    if obj: unreal.EditorLevelLibrary.spawn_actor_from_object(obj,unreal.Vector(*loc))

sun=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000))
sun.set_actor_rotation(unreal.Rotator(-35,-25,0),False)
unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,600))
unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(0,0,0))
unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-650,0,120))
unreal.EditorLevelLibrary.save_current_level()
unreal.EditorAssetLibrary.save_directory(MAP_DIR,only_if_is_dirty=False,recursive=True)
unreal.log("NARIS_AUTOMATION_SUCCESS")
