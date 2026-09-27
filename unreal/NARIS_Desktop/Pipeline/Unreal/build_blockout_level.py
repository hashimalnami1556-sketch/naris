import unreal

LEVEL="/Game/Maps/NARIS_Blockout"
ASSETS={
 "ground":"/Game/Art/Imported/ENV_AshenGround.ENV_AshenGround",
 "hero":"/Game/Art/Imported/CHR_AshenVessel_Blockout.CHR_AshenVessel_Blockout",
 "wolf":"/Game/Art/Imported/CHR_CelestialWolf_Blockout.CHR_CelestialWolf_Blockout",
 "enemy":"/Game/Art/Imported/ENM_BoneBeast_Blockout.ENM_BoneBeast_Blockout",
 "pillar1":"/Game/Art/Imported/ENV_GatePillar.ENV_GatePillar",
 "pillar2":"/Game/Art/Imported/ENV_GatePillar_001.ENV_GatePillar_001",
 "lintel":"/Game/Art/Imported/ENV_GateLintel.ENV_GateLintel"
}
unreal.EditorAssetLibrary.make_directory("/Game/Maps")
world=unreal.EditorLevelLibrary.new_level(LEVEL)
placements=[
 ("ground",(0,0,0)),
 ("hero",(0,0,90)),
 ("wolf",(220,0,55)),
 ("enemy",(500,0,125)),
 ("pillar1",(-350,700,250)),
 ("pillar2",(350,700,250)),
 ("lintel",(0,700,500))
]
for key,loc in placements:
    asset=unreal.load_asset(ASSETS[key])
    if asset:
        unreal.EditorLevelLibrary.spawn_actor_from_object(asset, unreal.Vector(*loc))
# light
sun=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,800))
sun.set_actor_rotation(unreal.Rotator(-35,-30,0), False)
sky=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,500))
unreal.EditorLevelLibrary.save_current_level()
unreal.log("NARIS_BLOCKOUT_LEVEL_CREATED")
