"""Unreal Engine 5.7: import and place native Fiery Demon in an isolated QA map.
Requires compiled ANarisFieryDemonBoss and FBX exported from 11-clip GLB.
Not a PIE test, benchmark or shipping build.
"""
import os, json
from pathlib import Path
import unreal

QA_MAP = "/Game/NARIS/W04/Maps/L_FieryDemon_QA"
DEST = "/Game/NARIS/Enemies/FieryDemon"
ENV_DEST = "/Game/NARIS/W04/Environments/FieryDemonQA"
BOSS_CLASS = "/Script/NARIS_W04.NarisFieryDemonBoss"
ACTOR_LABEL = "NARIS_FieryDemon_EliteBoss"

def fail(msg):
    unreal.log_error("[NARIS_FIERY_DEMON] "+msg)
    raise RuntimeError(msg)

def import_fbx(path, folder, skeletal=False):
    source=Path(path)
    if not source.is_file(): fail("Missing FBX: "+str(source))
    task=unreal.AssetImportTask()
    task.filename=str(source)
    task.destination_path=folder
    task.automated=True
    task.save=True
    # Re-import into this dedicated W04 boss folder rather than creating _1 duplicates.
    task.replace_existing=True
    options=unreal.FbxImportUI()
    options.import_mesh=True
    options.import_as_skeletal=bool(skeletal)
    options.import_animations=bool(skeletal)
    options.import_materials=True
    options.import_textures=True
    options.mesh_type_to_import=(unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal
                                 else unreal.FBXImportType.FBXIT_STATIC_MESH)
    task.options=options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    paths=list(task.imported_object_paths)
    return paths,[unreal.load_asset(path) for path in paths]

def actor_by_label(actors,label):
    return next((actor for actor in actors.get_all_level_actors()
                 if actor.get_actor_label()==label),None)

def spawn_once(actors,cls,label,pos):
    actor=actor_by_label(actors,label)
    if actor:return actor
    actor=actors.spawn_actor_from_class(cls,unreal.Vector(*pos),unreal.Rotator(0,0,0))
    if not actor:fail("Actor spawn failed: "+label)
    actor.set_actor_label(label)
    return actor

def open_level(target):
    exists=unreal.EditorAssetLibrary.does_asset_exist(target)
    if target!=QA_MAP and not exists:
        fail("Refusing to modify production: missing map "+target)
    if exists:
        if not unreal.EditorLoadingAndSavingUtils.load_map(target):
            fail("Failed to load "+target)
    elif not unreal.EditorLevelLibrary.new_level(target):
        fail("Failed to create QA level")

def choose_animation(animation_names,*hints):
    for hint in hints:
        for name,value in animation_names.items():
            if hint in name.lower():return value
    return None

def place_ground_and_player(actors):
    spawn_once(actors,unreal.PlayerStart,"NARIS_QA_PlayerStart",(-450,0,150))
    ground=spawn_once(actors,unreal.StaticMeshActor,"NARIS_QA_CollisionFloor",(0,0,-150))
    cube=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if not cube:fail("No Engine BasicShapes Cube for collision ground")
    component=ground.get_editor_property("static_mesh_component")
    if hasattr(component,"set_static_mesh"):component.set_static_mesh(cube)
    else:component.set_editor_property("static_mesh",cube)
    ground.set_actor_scale3d(unreal.Vector(40,40,0.5))

def place_environment(actors,fbx):
    if not fbx:return
    _,assets=import_fbx(fbx,ENV_DEST,False)
    meshes=[a for a in assets if isinstance(a,unreal.StaticMesh)]
    if not meshes:fail("Environment did not import StaticMesh")
    actor=spawn_once(actors,unreal.StaticMeshActor,"NARIS_AshGate_Environment",(0,0,-120))
    component=actor.get_editor_property("static_mesh_component")
    if hasattr(component,"set_static_mesh"):component.set_static_mesh(meshes[0])
    else:component.set_editor_property("static_mesh",meshes[0])

def spawn_boss_position(actors,target):
    if target==QA_MAP:
        return (450,0,130)
    # Do not inject an elite boss near the global origin or player spawn.
    anchor=actor_by_label(actors,"NARIS_AshGate_0001")
    if not anchor:
        fail("Missing production Ash Gate anchor NARIS_AshGate_0001; no map saved")
    origin=anchor.get_actor_location()
    forward=anchor.get_actor_forward_vector()
    return tuple(origin + forward * 650 + unreal.Vector(0,0,120))


def place_boss(actors,mesh,animations,target):
    position=spawn_boss_position(actors,target)
    boss_class=unreal.load_class(None,BOSS_CLASS)
    if not boss_class:fail("Native Fiery Demon boss class missing; compile NARIS_W04Editor")
    boss=spawn_once(actors,boss_class,ACTOR_LABEL,position)
    if not boss.get_class().is_child_of(boss_class):
        fail("Existing actor with same label is not Fiery Demon Boss")
    comp=boss.get_mesh()
    if hasattr(comp,"set_skeletal_mesh_asset"):comp.set_skeletal_mesh_asset(mesh)
    else:comp.set_editor_property("skeletal_mesh",mesh)
    names={a.get_name().lower():a for a in animations}
    binding=[
        ("idle_animation",choose_animation(names,"idle","breath")),
        ("smash_animation",choose_animation(names,"groundsmash","clawswipe")),
        ("nova_animation",choose_animation(names,"embernova","flame")),
        ("enrage_animation",choose_animation(names,"enrage")),
        ("death_animation",choose_animation(names,"death","defeat","die"))]
    if any(a is None for _,a in binding[:3]):
        fail("Required boss attack animations missing; no map saved")
    for name,anim in binding:
        if anim is not None:boss.set_editor_property(name,anim)
    return boss,{k:a.get_name() for k,a in binding if a is not None}

def main():
    target=os.environ.get("NARIS_TARGET_MAP",QA_MAP).strip() or QA_MAP
    if target!=QA_MAP and os.environ.get("NARIS_ALLOW_MAP_EDIT")!="1":
        fail("Refusing to modify production map without NARIS_ALLOW_MAP_EDIT=1")
    source=os.environ.get("NARIS_DEMON_FBX","")
    if not source:fail("Set NARIS_DEMON_FBX")
    imported,assets=import_fbx(source,DEST,True)
    meshes=[a for a in assets if isinstance(a,unreal.SkeletalMesh)]
    animation_assets=[a for a in assets if isinstance(a,unreal.AnimSequence)]
    if not meshes or not animation_assets:
        fail("SkeletalMesh or AnimSequences missing; map not saved")
    names={a.get_name().lower():a for a in animation_assets}
    for hints in (("idle","breath"),("groundsmash","clawswipe"),("embernova","flame")):
        if not choose_animation(names,*hints):fail("Required animation missing")
    open_level(target)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if target==QA_MAP:
        place_ground_and_player(actors)
        place_environment(actors,os.environ.get("NARIS_ENV_FBX",""))
        spawn_once(actors,unreal.DirectionalLight,"NARIS_QA_Sun",(0,0,800))
    boss,bindings=place_boss(actors,meshes[0],animation_assets,target)
    unreal.EditorLevelLibrary.save_current_level()
    report={"status":"editor_map_saved","map":target,"boss":boss.get_path_name(),
        "mesh":meshes[0].get_path_name(),"animations_imported":len(animation_assets),
        "animation_bindings":bindings,"imported_assets":imported,
        "pie_tested":False,"shipping_approved":False}
    target_report=os.environ.get("NARIS_REPORT_JSON")
    if target_report:
        dest=Path(target_report)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,indent=2),encoding="utf-8")
    unreal.log("[NARIS_FIERY_DEMON] "+json.dumps(report))
    return report

if __name__=="__main__":main()
