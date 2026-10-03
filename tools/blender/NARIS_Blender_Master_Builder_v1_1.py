# -*- coding: utf-8 -*-
"""
NARIS Blender Master Builder v1.0
Production-oriented Blender 4.x add-on for CALL OF NARIS.

Goals:
- Build a deterministic NARIS production scene structure.
- Generate prototype hero/companion/enemy/weapon/environment assets.
- Add armature, simple actions, sockets, collision and LODs.
- Validate common production issues.
- Export per-engine packages for Unreal / Godot / Unity.

Important:
This add-on is an AUTHORING / ASSET PIPELINE tool. Gameplay runtime remains in the game engine.
"""

bl_info = {
    "name": "NARIS Blender Master Builder",
    "author": "NARIS Studios / Alnami Company",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > NARIS",
    "description": "NARIS production builder: assets, rigs, animation, LOD, collision, validation and engine export",
    "category": "3D View",
}

# Canonical W04 production contract integration (v1.1)
# Unreal Engine 5.4 is authoritative. These IDs are immutable registry identities.
CANONICAL_ENGINE_TARGET = "Unreal Engine 5.4"
MASTER_ASSET_REGISTRY = "data/MASTER_ASSET_REGISTRY.json"
PRODUCTION_BINDINGS = "unreal/NARIS_W04/Content/NARIS/W04/Production/W04_ProductionAssetBindings.json"
ENVIRONMENT_FACTORY_CONTRACT = "data/environments/W04_AshenForest_environment_factory_v2.json"
REGISTRY_GATED_EXPORTER = "tools/blender/naris_export.py"
W04_CORE_ASSETS = {
    "hero": {"naris_asset_id": "NARIS-W04-CHR-HERO-0001", "expected_unreal_object_path": "/Game/NARIS/W04/Characters/Hero/SK_AshenVessel.SK_AshenVessel"},
    "celestial_wolf": {"naris_asset_id": "NARIS-W04-CHR-COMPANION-0001", "expected_unreal_object_path": "/Game/NARIS/W04/Characters/CelestialWolf/SK_CelestialWolf.SK_CelestialWolf"},
    "bone_beast": {"naris_asset_id": "NARIS-W04-ENM-BONEBEAST-0001", "expected_unreal_object_path": "/Game/NARIS/W04/Bosses/BoneBeast/SK_BoneBeast.SK_BoneBeast"},
    "sword_of_poem": {"naris_asset_id": "NARIS-W04-WPN-SWORD-0001", "expected_unreal_object_path": "/Game/NARIS/W04/Weapons/SwordOfPoem/SM_SwordOfPoem.SM_SwordOfPoem"},
}

def load_w04_contract(repo_root):
    import json
    from pathlib import Path
    root = Path(repo_root)
    registry = json.loads((root / MASTER_ASSET_REGISTRY).read_text(encoding="utf-8"))
    bindings = json.loads((root / PRODUCTION_BINDINGS).read_text(encoding="utf-8"))
    environment = json.loads((root / ENVIRONMENT_FACTORY_CONTRACT).read_text(encoding="utf-8"))
    registered = {x.get("id"): x for x in registry.get("assets", []) if isinstance(x, dict)}
    bound = {x.get("asset_id"): x for x in bindings.get("assets", []) if isinstance(x, dict)}
    for spec in W04_CORE_ASSETS.values():
        aid = spec["naris_asset_id"]
        if aid not in registered:
            raise RuntimeError(f"Unregistered canonical asset: {aid}")
        if aid not in bound:
            raise RuntimeError(f"Missing W04 production binding: {aid}")
    return {
        "registry": registered,
        "bindings": bound,
        "grid_m": environment["grid_m"],
        "floor_module_m": environment["modular_units"]["floor"],
        "wall_height_m": environment["modular_units"]["height"],
        "streaming": environment["streaming"],
        "material_slots_max_per_mesh": environment["performance"]["material_slots_max_per_mesh"],
        "environment": environment,
    }

def stamp_w04_asset(obj, role, contract=None):
    spec = W04_CORE_ASSETS[role]
    obj["naris_asset_id"] = spec["naris_asset_id"]
    obj["naris_engine_target"] = CANONICAL_ENGINE_TARGET
    obj["expected_unreal_object_path"] = spec["expected_unreal_object_path"]
    obj["naris_registry_file"] = MASTER_ASSET_REGISTRY
    obj["naris_production_bindings"] = PRODUCTION_BINDINGS
    obj["naris_registry_gated_exporter"] = REGISTRY_GATED_EXPORTER
    if contract:
        binding = contract["bindings"][spec["naris_asset_id"]]
        obj["naris_min_lods"] = int(binding.get("min_lods", 1))
        obj["naris_material_slots_max"] = int(binding.get("max_material_slots", contract["material_slots_max_per_mesh"]))
    return obj


import bpy
import math
import os
import json
import random
import traceback
from pathlib import Path
from mathutils import Vector
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty

# -----------------------------------------------------------------------------
# Constants / project definition
# -----------------------------------------------------------------------------
ADDON_VERSION = "1.0.0"
PROJECT_NAME = "CALL_OF_NARIS"
DEFAULT_OUTPUT = os.path.join(os.path.expanduser("~"), "NARIS_BlenderOutput")

COLLECTIONS = [
    "NARIS_ROOT",
    "CHARACTERS",
    "COMPANIONS",
    "ENEMIES",
    "BOSSES",
    "WEAPONS",
    "ENVIRONMENT",
    "PROPS",
    "VFX_PREVIEW",
    "COLLISION",
    "LODS",
    "SOCKETS",
    "CAMERAS",
    "LIGHTS",
    "EXPORT",
]

NARIS_PALETTE = {
    "ash_black": (0.02, 0.03, 0.05, 1.0),
    "burned_steel": (0.10, 0.12, 0.16, 1.0),
    "ember_orange": (1.0, 0.22, 0.035, 1.0),
    "ember_crimson": (0.35, 0.015, 0.02, 1.0),
    "aether_violet": (0.34, 0.07, 0.70, 1.0),
    "mist_cyan": (0.10, 0.70, 1.0, 1.0),
    "ancient_gold": (0.66, 0.42, 0.10, 1.0),
    "spirit_green": (0.10, 0.80, 0.32, 1.0),
    "bone": (0.55, 0.50, 0.40, 1.0),
}

ENGINE_EXPORTS = {
    "UNREAL": {"folder": "unreal", "ext": ".fbx"},
    "GODOT": {"folder": "godot", "ext": ".glb"},
    "UNITY": {"folder": "unity", "ext": ".fbx"},
}

# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------
def log(msg):
    print(f"[NARIS] {msg}")


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def safe_remove_object(obj):
    if obj and obj.name in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def get_or_create_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
    if parent is None:
        root = bpy.context.scene.collection
        if col.name not in root.children:
            try:
                root.children.link(col)
            except RuntimeError:
                pass
    else:
        if col.name not in parent.children:
            try:
                parent.children.link(col)
            except RuntimeError:
                pass
    return col


def move_to_collection(obj, collection_name):
    target = get_or_create_collection(collection_name)
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    target.objects.link(obj)
    return obj


def set_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def tag(obj, **kwargs):
    for k, v in kwargs.items():
        obj[k] = v
    return obj


def clean_scene(keep_world=True):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.armatures,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.materials,
        bpy.data.node_groups,
    ):
        for item in list(block):
            if item.users == 0:
                block.remove(item)
    # remove only our generated collections
    for name in COLLECTIONS:
        col = bpy.data.collections.get(name)
        if col and col.users == 0:
            bpy.data.collections.remove(col)
    if not keep_world and bpy.context.scene.world:
        bpy.data.worlds.remove(bpy.context.scene.world)


def setup_scene_defaults(scene):
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = 60
    scene.frame_start = 1
    scene.frame_end = 240
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        pass
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0


def build_collection_tree():
    root = get_or_create_collection("NARIS_ROOT")
    for name in COLLECTIONS:
        if name == "NARIS_ROOT":
            continue
        get_or_create_collection(name, root)
    return root


def make_material(name, base_color, metallic=0.0, roughness=0.5, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = base_color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if emission is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def add_primitive(kind, name, location=(0, 0, 0), scale=(1, 1, 1), rotation=(0, 0, 0), material=None, collection=None):
    if kind == "cube":
        bpy.ops.mesh.primitive_cube_add(size=2, location=location, rotation=rotation)
    elif kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=location, rotation=rotation)
    elif kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=2, location=location, rotation=rotation)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1, radius2=0.0, depth=2, location=location, rotation=rotation)
    elif kind == "plane":
        bpy.ops.mesh.primitive_plane_add(size=2, location=location, rotation=rotation)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.25, location=location, rotation=rotation)
    else:
        raise ValueError(f"Unsupported primitive: {kind}")
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if material and hasattr(obj.data, "materials"):
        obj.data.materials.append(material)
    if collection:
        move_to_collection(obj, collection)
    return obj


def add_empty(name, location=(0, 0, 0), empty_type="PLAIN_AXES", collection="SOCKETS"):
    bpy.ops.object.empty_add(type=empty_type, location=location)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, collection)
    return obj


def set_smooth(obj):
    if not obj or obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True


def apply_transforms(obj, location=False, rotation=True, scale=True):
    if not obj:
        return
    set_active(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def ensure_world():
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("NARIS_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.008, 0.012, 0.02, 1)
        bg.inputs[1].default_value = 0.16
    return world

# -----------------------------------------------------------------------------
# Materials / lookdev
# -----------------------------------------------------------------------------
def create_naris_materials():
    mats = {
        "MAT_AshBlack": make_material("MAT_AshBlack", NARIS_PALETTE["ash_black"], metallic=0.1, roughness=0.8),
        "MAT_BurnedSteel": make_material("MAT_BurnedSteel", NARIS_PALETTE["burned_steel"], metallic=0.85, roughness=0.32),
        "MAT_Ember": make_material("MAT_Ember", (0.22, 0.015, 0.005, 1), metallic=0.1, roughness=0.35,
                                    emission=NARIS_PALETTE["ember_orange"], emission_strength=5.0),
        "MAT_Aether": make_material("MAT_Aether", (0.03, 0.04, 0.10, 1), metallic=0.15, roughness=0.25,
                                     emission=NARIS_PALETTE["aether_violet"], emission_strength=4.0),
        "MAT_MistCyan": make_material("MAT_MistCyan", (0.02, 0.08, 0.12, 1), roughness=0.2,
                                       emission=NARIS_PALETTE["mist_cyan"], emission_strength=4.0),
        "MAT_AncientGold": make_material("MAT_AncientGold", NARIS_PALETTE["ancient_gold"], metallic=0.9, roughness=0.24),
        "MAT_Bone": make_material("MAT_Bone", NARIS_PALETTE["bone"], metallic=0.0, roughness=0.72),
        "MAT_Crimson": make_material("MAT_Crimson", NARIS_PALETTE["ember_crimson"], metallic=0.0, roughness=0.72),
        "MAT_Ground": make_material("MAT_Ground", (0.035, 0.04, 0.045, 1), metallic=0.0, roughness=0.96),
    }
    return mats

# -----------------------------------------------------------------------------
# Character / companion / enemy factories
# -----------------------------------------------------------------------------
def create_root(name, location, collection):
    root = add_empty(name, location, "PLAIN_AXES", collection)
    tag(root, naris_role="ROOT", asset_name=name)
    return root


def parent_all(root, objects):
    for obj in objects:
        if obj:
            obj.parent = root


def create_ashen_vessel(mats):
    root = create_root("CHR_AshenVessel_ROOT", (0, 0, 0), "CHARACTERS")
    parts = []
    parts.append(add_primitive("cylinder", "CHR_AshenVessel_Torso", (0, 0, 1.45), (0.34, 0.24, 0.48), material=mats["MAT_BurnedSteel"], collection="CHARACTERS"))
    parts.append(add_primitive("sphere", "CHR_AshenVessel_Head", (0, 0, 2.28), (0.22, 0.20, 0.27), material=mats["MAT_AshBlack"], collection="CHARACTERS"))
    parts.append(add_primitive("cube", "CHR_AshenVessel_Cape", (0, 0.17, 1.45), (0.45, 0.035, 0.62), rotation=(math.radians(-8),0,0), material=mats["MAT_Crimson"], collection="CHARACTERS"))
    for side, x in (("L", -0.46), ("R", 0.46)):
        parts.append(add_primitive("cylinder", f"CHR_AshenVessel_Arm_{side}", (x, 0, 1.5), (0.10,0.10,0.46), material=mats["MAT_BurnedSteel"], collection="CHARACTERS"))
        parts.append(add_primitive("cylinder", f"CHR_AshenVessel_Leg_{side}", (x*0.45, 0, 0.62), (0.13,0.13,0.58), material=mats["MAT_AshBlack"], collection="CHARACTERS"))
    eye = add_primitive("sphere", "CHR_AshenVessel_EyeGlow_L", (-0.075, -0.18, 2.30), (0.035,0.02,0.035), material=mats["MAT_Ember"], collection="CHARACTERS")
    parts.append(eye)
    parent_all(root, parts)
    tag(root, naris_asset="AshenVessel", naris_type="CHARACTER", export=True)
    create_humanoid_armature(root)
    create_character_sockets(root)
    return root


def create_celestial_wolf(mats):
    root = create_root("CMP_CelestialWolf_ROOT", (2.6, -0.3, 0), "COMPANIONS")
    body = add_primitive("sphere", "CMP_CelestialWolf_Body", (2.6,0,1.0), (0.85,0.33,0.42), material=mats["MAT_MistCyan"], collection="COMPANIONS")
    head = add_primitive("sphere", "CMP_CelestialWolf_Head", (2.6,-0.68,1.28), (0.40,0.32,0.34), material=mats["MAT_MistCyan"], collection="COMPANIONS")
    tail = add_primitive("cone", "CMP_CelestialWolf_Tail", (2.6,0.80,1.08), (0.22,0.22,0.78), rotation=(math.radians(78),0,0), material=mats["MAT_Aether"], collection="COMPANIONS")
    parts=[body,head,tail]
    for side,x in (("L",-0.33),("R",0.33)):
        for front,y in (("F",-0.40),("B",0.40)):
            leg=add_primitive("cylinder",f"CMP_CelestialWolf_Leg_{front}{side}",(2.6+x,y,0.48),(0.09,0.09,0.45),material=mats["MAT_MistCyan"],collection="COMPANIONS")
            parts.append(leg)
    parent_all(root,parts)
    tag(root,naris_asset="CelestialWolf",naris_type="COMPANION",export=True)
    return root


def create_bone_beast(mats, location=(-3.2, 3.5, 0)):
    root = create_root("ENM_BoneBeast_ROOT", location, "ENEMIES")
    x,y,z=location
    rib = add_primitive("torus","ENM_BoneBeast_RibCage",(x,y,z+1.7),(0.95,0.50,1.1),rotation=(math.radians(90),0,0),material=mats["MAT_Bone"],collection="ENEMIES")
    skull=add_primitive("sphere","ENM_BoneBeast_Skull",(x,y-0.7,z+2.25),(0.55,0.42,0.46),material=mats["MAT_Bone"],collection="ENEMIES")
    core=add_primitive("sphere","ENM_BoneBeast_CorruptedCore",(x,y-0.02,z+1.68),(0.24,0.20,0.26),material=mats["MAT_Aether"],collection="ENEMIES")
    parts=[rib,skull,core]
    for side,sx in (("L",-0.78),("R",0.78)):
        arm=add_primitive("cylinder",f"ENM_BoneBeast_Arm_{side}",(x+sx,y,z+1.5),(0.18,0.18,0.76),material=mats["MAT_Bone"],collection="ENEMIES")
        leg=add_primitive("cylinder",f"ENM_BoneBeast_Leg_{side}",(x+sx*0.55,y,z+0.62),(0.22,0.22,0.63),material=mats["MAT_Bone"],collection="ENEMIES")
        parts += [arm,leg]
    parent_all(root,parts)
    tag(root,naris_asset="BoneBeast",naris_type="ENEMY",hp=180,poise=100,export=True)
    create_enemy_sockets(root)
    return root

# -----------------------------------------------------------------------------
# Weapons
# -----------------------------------------------------------------------------
def create_sword_of_poem(mats, location=(0.85, 0.0, 1.2)):
    root=create_root("WPN_SwordOfPoem_ROOT",location,"WEAPONS")
    x,y,z=location
    blade=add_primitive("cube","WPN_SwordOfPoem_Blade",(x,y,z+0.65),(0.075,0.035,0.68),material=mats["MAT_BurnedSteel"],collection="WEAPONS")
    edge=add_primitive("cube","WPN_SwordOfPoem_EmberEdge",(x-0.07,y,z+0.65),(0.018,0.025,0.66),material=mats["MAT_Ember"],collection="WEAPONS")
    guard=add_primitive("cube","WPN_SwordOfPoem_Guard",(x,y,z-0.02),(0.30,0.06,0.05),material=mats["MAT_AncientGold"],collection="WEAPONS")
    grip=add_primitive("cylinder","WPN_SwordOfPoem_Grip",(x,y,z-0.30),(0.06,0.06,0.28),material=mats["MAT_AshBlack"],collection="WEAPONS")
    parent_all(root,[blade,edge,guard,grip])
    tag(root,naris_asset="SwordOfPoem",naris_type="WEAPON",damage=35,energy="NARIS_FLAME",export=True)
    add_empty("SOCKET_WPN_Tip",(x,y,z+1.34),collection="SOCKETS").parent=root
    add_empty("SOCKET_WPN_Hilt",(x,y,z-0.32),collection="SOCKETS").parent=root
    return root

# -----------------------------------------------------------------------------
# Rigging / animation
# -----------------------------------------------------------------------------
def create_humanoid_armature(character_root):
    bpy.ops.object.armature_add(enter_editmode=True, location=character_root.location)
    arm=bpy.context.object
    arm.name="RIG_AshenVessel"
    move_to_collection(arm,"CHARACTERS")
    arm.show_in_front=True
    eb=arm.data.edit_bones
    base=eb[0]
    base.name="root"
    base.head=(0,0,0)
    base.tail=(0,0,0.25)
    def bone(name,head,tail,parent=None):
        b=eb.new(name); b.head=head; b.tail=tail
        if parent: b.parent=parent
        return b
    pelvis=bone("pelvis",(0,0,0.9),(0,0,1.15),base)
    spine=bone("spine_01",(0,0,1.15),(0,0,1.65),pelvis)
    chest=bone("spine_02",(0,0,1.65),(0,0,2.0),spine)
    neck=bone("neck",(0,0,2.0),(0,0,2.18),chest)
    head=bone("head",(0,0,2.18),(0,0,2.55),neck)
    for side,sign in (("L",-1),("R",1)):
        ua=bone(f"upper_arm.{side}",(0.20*sign,0,1.92),(0.62*sign,0,1.70),chest)
        fa=bone(f"forearm.{side}",(0.62*sign,0,1.70),(0.88*sign,0,1.48),ua)
        bone(f"hand.{side}",(0.88*sign,0,1.48),(1.00*sign,0,1.40),fa)
        th=bone(f"thigh.{side}",(0.16*sign,0,0.95),(0.20*sign,0,0.48),pelvis)
        sh=bone(f"shin.{side}",(0.20*sign,0,0.48),(0.20*sign,-0.02,0.08),th)
        bone(f"foot.{side}",(0.20*sign,-0.02,0.08),(0.20*sign,-0.26,0.03),sh)
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.parent=character_root
    tag(arm,naris_type="RIG",asset="AshenVessel")
    create_basic_actions(arm)
    return arm


def create_basic_actions(arm):
    # Non-destructive action authoring; clear animation after storing actions.
    actions=[]
    for name,start,end in (("AV_Idle",1,60),("AV_Walk",1,32),("AV_Attack_Light",1,24),("AV_Dodge",1,20)):
        action=bpy.data.actions.get(name) or bpy.data.actions.new(name)
        action["naris_frame_start"]=start
        action["naris_frame_end"]=end
        actions.append(action)
    # Key a simple walk if pose bones exist.
    walk=bpy.data.actions.get("AV_Walk")
    arm.animation_data_create(); arm.animation_data.action=walk
    pb=arm.pose.bones
    for f,angle in ((1,0.45),(9,-0.45),(17,0.45),(25,-0.45),(32,0.45)):
        for bn,mul in (("thigh.L",1),("thigh.R",-1),("upper_arm.L",-1),("upper_arm.R",1)):
            if bn in pb:
                b=pb[bn]; b.rotation_mode="XYZ"; b.rotation_euler[0]=angle*mul; b.keyframe_insert("rotation_euler",frame=f)
    arm.animation_data.action=None
    return actions


def create_character_sockets(root):
    for name,loc in {
        "SOCKET_Weapon_R": (0.62,-0.02,1.38),
        "SOCKET_Weapon_L": (-0.62,-0.02,1.38),
        "SOCKET_Back": (0,0.20,1.75),
        "SOCKET_HeadFX": (0,0,2.52),
        "SOCKET_HandFX_R": (0.92,0,1.42),
        "SOCKET_HandFX_L": (-0.92,0,1.42),
        "SOCKET_FootFX_R": (0.20,0,0.04),
        "SOCKET_FootFX_L": (-0.20,0,0.04),
    }.items():
        s=add_empty(name,Vector(root.location)+Vector(loc),collection="SOCKETS")
        s.parent=root
        tag(s,naris_socket=True)


def create_enemy_sockets(root):
    for name,loc in {
        "SOCKET_BoneBeast_Core": (0,0,1.7),
        "SOCKET_BoneBeast_Mouth": (0,-0.8,2.25),
        "SOCKET_BoneBeast_BackFX": (0,0.3,2.3),
    }.items():
        s=add_empty(name,Vector(root.location)+Vector(loc),collection="SOCKETS")
        s.parent=root
        tag(s,naris_socket=True)

# -----------------------------------------------------------------------------
# Environment / GN / VFX preview
# -----------------------------------------------------------------------------
def create_ashen_forest(mats, seed=1337):
    random.seed(seed)
    ground=add_primitive("plane","ENV_AshenForest_Ground",(0,3,0),(14,14,1),material=mats["MAT_Ground"],collection="ENVIRONMENT")
    tag(ground,naris_asset="AshenForest",surface="ASH",export=True)
    # rocks / trees
    for i in range(36):
        x=random.uniform(-12,12); y=random.uniform(-4,16)
        if i<20:
            trunk=add_primitive("cylinder",f"ENV_DeadTree_{i:02d}",(x,y,random.uniform(1.2,2.2)),(random.uniform(.15,.28),random.uniform(.15,.28),random.uniform(1.2,2.2)),rotation=(random.uniform(-.12,.12),random.uniform(-.12,.12),random.uniform(-.2,.2)),material=mats["MAT_AshBlack"],collection="ENVIRONMENT")
            tag(trunk,naris_prop="dead_tree")
        else:
            rock=add_primitive("sphere",f"ENV_AshRock_{i:02d}",(x,y,random.uniform(.15,.5)),(random.uniform(.3,1),random.uniform(.3,.8),random.uniform(.2,.7)),material=mats["MAT_Ground"],collection="ENVIRONMENT")
            tag(rock,naris_prop="rock")
    create_rune_gate(mats,(0,10,0))
    create_waystone(mats,(-5,4,0))
    create_ash_particles_preview(mats)
    return ground


def create_rune_gate(mats, location):
    x,y,z=location
    root=create_root("ENV_AshGate_ROOT",location,"ENVIRONMENT")
    left=add_primitive("cube","ENV_AshGate_Pillar_L",(x-2,y,z+2.6),(0.65,0.75,2.6),material=mats["MAT_Ground"],collection="ENVIRONMENT")
    right=add_primitive("cube","ENV_AshGate_Pillar_R",(x+2,y,z+2.6),(0.65,0.75,2.6),material=mats["MAT_Ground"],collection="ENVIRONMENT")
    top=add_primitive("cube","ENV_AshGate_Lintel",(x,y,z+5.15),(2.65,0.8,0.55),material=mats["MAT_Ground"],collection="ENVIRONMENT")
    rune=add_primitive("torus","ENV_AshGate_Rune",(x,y-0.76,z+2.7),(1.2,1.2,1.2),rotation=(math.radians(90),0,0),material=mats["MAT_Aether"],collection="ENVIRONMENT")
    parent_all(root,[left,right,top,rune])
    tag(root,naris_asset="AshGate",interaction="LOCKED_GATE",export=True)
    return root


def create_waystone(mats, location):
    x,y,z=location
    stone=add_primitive("cylinder","ENV_Waystone",(x,y,z+1.0),(0.45,0.45,1.0),material=mats["MAT_Ground"],collection="ENVIRONMENT")
    core=add_primitive("sphere","ENV_Waystone_Core",(x,y,z+1.45),(0.18,0.18,0.18),material=mats["MAT_Ember"],collection="VFX_PREVIEW")
    core.parent=stone
    tag(stone,naris_asset="Waystone",interaction="CHECKPOINT",export=True)
    return stone


def create_ash_particles_preview(mats):
    # Lightweight viewport preview: floating ash motes as instanced ico spheres.
    for i in range(60):
        p=add_primitive("sphere",f"VFX_AshMote_{i:03d}",(random.uniform(-10,10),random.uniform(-3,14),random.uniform(.2,6)),(0.015,0.015,0.015),material=mats["MAT_Ember"] if i%13==0 else mats["MAT_Ground"],collection="VFX_PREVIEW")
        tag(p,naris_preview=True,export=False)

# -----------------------------------------------------------------------------
# Lighting / camera
# -----------------------------------------------------------------------------
def add_light(name, light_type, location, energy, color, size=4.0, collection="LIGHTS"):
    bpy.ops.object.light_add(type=light_type, location=location)
    obj=bpy.context.object; obj.name=name; obj.data.energy=energy; obj.data.color=color
    if hasattr(obj.data,"shape") and light_type=="AREA":
        obj.data.shape="DISK"; obj.data.size=size
    move_to_collection(obj,collection)
    return obj


def create_lighting_and_camera():
    add_light("LGT_Key_Ember","AREA",(4,-4,6),1200,(1.0,0.20,0.04),5)
    add_light("LGT_Rim_Cyan","AREA",(-5,3,5),900,(0.05,0.55,1.0),4)
    add_light("LGT_Gate_Violet","POINT",(0,9.2,3),700,(0.35,0.05,1.0),2)
    bpy.ops.object.camera_add(location=(9,-12,6.4))
    cam=bpy.context.object; cam.name="CAM_NARIS_Master"; cam.data.lens=48
    move_to_collection(cam,"CAMERAS")
    target=add_empty("CAM_Target",(0,3,1.6),collection="CAMERAS")
    c=cam.constraints.new(type="TRACK_TO"); c.target=target; c.track_axis="TRACK_NEGATIVE_Z"; c.up_axis="UP_Y"
    bpy.context.scene.camera=cam
    return cam

# -----------------------------------------------------------------------------
# Collision / LOD tools
# -----------------------------------------------------------------------------
def mesh_descendants(root):
    out=[]
    def walk(obj):
        for ch in obj.children:
            if ch.type=="MESH": out.append(ch)
            walk(ch)
    walk(root)
    return out


def duplicate_mesh_object(obj, name, collection):
    cp=obj.copy(); cp.data=obj.data.copy(); cp.name=name
    get_or_create_collection(collection).objects.link(cp)
    cp.matrix_world=obj.matrix_world.copy()
    return cp


def generate_lods_for_root(root, ratios=(0.55,0.25,0.10)):
    generated=[]
    for src in mesh_descendants(root):
        for idx,ratio in enumerate(ratios, start=1):
            lod=duplicate_mesh_object(src,f"{src.name}_LOD{idx}","LODS")
            lod["naris_lod_level"]=idx
            lod["naris_lod_source"]=src.name
            mod=lod.modifiers.new(name=f"NARIS_Decimate_{idx}",type="DECIMATE")
            mod.ratio=ratio
            generated.append(lod)
    return generated


def generate_simple_collisions_for_root(root):
    made=[]
    for src in mesh_descendants(root):
        if src.get("naris_collision"):
            continue
        col=duplicate_mesh_object(src,f"UCX_{src.name}","COLLISION")
        # Use decimation as a cheap safe proxy. Engine can auto-convex later.
        mod=col.modifiers.new("NARIS_Collision_Decimate","DECIMATE"); mod.ratio=0.08
        col.display_type="WIRE"; col.hide_render=True
        col["naris_collision"]=True; col["export_collision"]=True
        made.append(col)
    return made

# -----------------------------------------------------------------------------
# Validation / manifests
# -----------------------------------------------------------------------------
def object_triangle_count(obj):
    if obj.type != "MESH": return 0
    try:
        return sum(max(0, len(p.vertices)-2) for p in obj.data.polygons)
    except Exception:
        return 0


def validate_scene():
    issues=[]
    seen=set()
    for obj in bpy.context.scene.objects:
        if obj.name in seen:
            issues.append({"severity":"ERROR","object":obj.name,"issue":"duplicate object name"})
        seen.add(obj.name)
        if obj.type=="MESH":
            if len(obj.data.polygons)==0:
                issues.append({"severity":"ERROR","object":obj.name,"issue":"mesh has no polygons"})
            if not obj.data.uv_layers:
                issues.append({"severity":"WARN","object":obj.name,"issue":"mesh has no UV map"})
            if len(obj.data.materials)==0:
                issues.append({"severity":"WARN","object":obj.name,"issue":"mesh has no material"})
            if any(abs(s-1.0)>0.001 for s in obj.scale):
                issues.append({"severity":"WARN","object":obj.name,"issue":"scale not applied"})
            tris=object_triangle_count(obj)
            if tris>120000:
                issues.append({"severity":"WARN","object":obj.name,"issue":f"high triangle count: {tris}"})
    required=["NARIS_ROOT","CHARACTERS","WEAPONS","ENVIRONMENT","COLLISION","LODS"]
    for name in required:
        if bpy.data.collections.get(name) is None:
            issues.append({"severity":"ERROR","object":"<scene>","issue":f"missing collection {name}"})
    return issues


def scene_manifest():
    assets=[]
    for obj in bpy.context.scene.objects:
        if obj.get("export",False) or obj.get("naris_asset"):
            assets.append({
                "name":obj.name,
                "type":obj.get("naris_type",obj.type),
                "asset":obj.get("naris_asset",""),
                "triangles":object_triangle_count(obj),
                "location":[round(v,4) for v in obj.location],
                "tags":{k:obj[k] for k in obj.keys() if str(k).startswith("naris_")},
            })
    return {
        "project":PROJECT_NAME,
        "addon_version":ADDON_VERSION,
        "blender_version":".".join(map(str,bpy.app.version)),
        "assets":assets,
        "validation":validate_scene(),
    }


def write_manifest(output_dir):
    ensure_dir(output_dir)
    path=os.path.join(output_dir,"naris_asset_manifest.json")
    with open(path,"w",encoding="utf-8") as f:
        json.dump(scene_manifest(),f,ensure_ascii=False,indent=2)
    return path

# -----------------------------------------------------------------------------
# Export
# -----------------------------------------------------------------------------
def export_selection_candidates():
    objs=[]
    for obj in bpy.context.scene.objects:
        if obj.hide_render and obj.get("naris_preview"):
            continue
        if obj.name.startswith("CAM_") or obj.name.startswith("LGT_"):
            continue
        if obj.get("naris_preview"):
            continue
        if obj.type in {"MESH","ARMATURE","EMPTY"}:
            objs.append(obj)
    return objs


def select_export_objects():
    bpy.ops.object.select_all(action="DESELECT")
    objs=export_selection_candidates()
    for obj in objs: obj.select_set(True)
    if objs: bpy.context.view_layer.objects.active=objs[0]
    return objs


def export_engine(engine, output_dir):
    engine=engine.upper()
    if engine not in ENGINE_EXPORTS:
        raise ValueError(engine)
    target=ensure_dir(os.path.join(output_dir,ENGINE_EXPORTS[engine]["folder"]))
    select_export_objects()
    if engine=="GODOT":
        path=os.path.join(target,"NARIS_Master.glb")
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True)
    else:
        path=os.path.join(target,"NARIS_Master.fbx")
        kwargs=dict(filepath=path,use_selection=True,apply_unit_scale=True,bake_space_transform=False,add_leaf_bones=False)
        if engine=="UNREAL":
            kwargs.update(axis_forward="-Y",axis_up="Z")
        else:
            kwargs.update(axis_forward="-Z",axis_up="Y")
        bpy.ops.export_scene.fbx(**kwargs)
    log(f"Exported {engine}: {path}")
    return path


def save_blend(output_dir):
    ensure_dir(output_dir)
    path=os.path.join(output_dir,"NARIS_Master_v1_0.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    return path

# -----------------------------------------------------------------------------
# Master build
# -----------------------------------------------------------------------------
def build_master_scene(scene=None, clear=True):
    scene=scene or bpy.context.scene
    if clear:
        clean_scene()
    setup_scene_defaults(scene)
    build_collection_tree()
    ensure_world()
    mats=create_naris_materials()
    create_ashen_forest(mats, seed=scene.naris_seed if hasattr(scene,"naris_seed") else 1337)
    hero=create_ashen_vessel(mats)
    wolf=create_celestial_wolf(mats)
    enemy=create_bone_beast(mats)
    sword=create_sword_of_poem(mats)
    # Canonical W04 identity is stamped at authoring time. Registry/binding validation
    # is enforced by load_w04_contract() when a repository root is supplied.
    stamp_w04_asset(hero, "hero")
    stamp_w04_asset(wolf, "celestial_wolf")
    stamp_w04_asset(enemy, "bone_beast")
    stamp_w04_asset(sword, "sword_of_poem")
    # Attach weapon to hero root for prototype authoring; actual socket mapping is exported as metadata.
    sword.parent=hero
    create_lighting_and_camera()
    log("Master scene built")
    return {"hero":hero,"wolf":wolf,"enemy":enemy,"weapon":sword}

# -----------------------------------------------------------------------------
# Operators
# -----------------------------------------------------------------------------
class NARIS_OT_build_master(bpy.types.Operator):
    bl_idname="naris.build_master"
    bl_label="Build NARIS Master Scene"
    bl_options={"REGISTER","UNDO"}
    def execute(self,context):
        try:
            build_master_scene(context.scene, clear=context.scene.naris_clear_before_build)
            self.report({"INFO"},"NARIS Master Scene built")
            return {"FINISHED"}
        except Exception as e:
            traceback.print_exc(); self.report({"ERROR"},str(e)); return {"CANCELLED"}


class NARIS_OT_generate_lods(bpy.types.Operator):
    bl_idname="naris.generate_lods"
    bl_label="Generate LODs"
    bl_options={"REGISTER","UNDO"}
    def execute(self,context):
        roots=[o for o in context.scene.objects if o.get("naris_asset") and o.get("export")]
        total=0
        for r in roots: total += len(generate_lods_for_root(r))
        self.report({"INFO"},f"Generated {total} LOD meshes")
        return {"FINISHED"}


class NARIS_OT_generate_collisions(bpy.types.Operator):
    bl_idname="naris.generate_collisions"
    bl_label="Generate Collisions"
    bl_options={"REGISTER","UNDO"}
    def execute(self,context):
        roots=[o for o in context.scene.objects if o.get("naris_asset") and o.get("export")]
        total=0
        for r in roots: total += len(generate_simple_collisions_for_root(r))
        self.report({"INFO"},f"Generated {total} collision proxies")
        return {"FINISHED"}


class NARIS_OT_validate(bpy.types.Operator):
    bl_idname="naris.validate_scene"
    bl_label="Validate Production Scene"
    def execute(self,context):
        issues=validate_scene()
        context.scene.naris_validation_summary=f"Issues: {len(issues)}"
        for issue in issues[:100]:
            log(f"{issue['severity']}: {issue['object']} - {issue['issue']}")
        if any(i["severity"]=="ERROR" for i in issues):
            self.report({"WARNING"},f"Validation found {len(issues)} issues; see console")
        else:
            self.report({"INFO"},f"Validation complete: {len(issues)} warnings/info")
        return {"FINISHED"}


class NARIS_OT_manifest(bpy.types.Operator):
    bl_idname="naris.write_manifest"
    bl_label="Write Manifest"
    def execute(self,context):
        path=write_manifest(context.scene.naris_output_dir)
        self.report({"INFO"},f"Manifest: {path}")
        return {"FINISHED"}


class NARIS_OT_export_engine(bpy.types.Operator):
    bl_idname="naris.export_engine"
    bl_label="Export Engine"
    engine: EnumProperty(name="Engine",items=[("UNREAL","Unreal",""),("GODOT","Godot",""),("UNITY","Unity","")])
    def execute(self,context):
        try:
            path=export_engine(self.engine,context.scene.naris_output_dir)
            write_manifest(context.scene.naris_output_dir)
            self.report({"INFO"},f"Exported: {path}")
            return {"FINISHED"}
        except Exception as e:
            traceback.print_exc(); self.report({"ERROR"},str(e)); return {"CANCELLED"}


class NARIS_OT_export_all(bpy.types.Operator):
    bl_idname="naris.export_all"
    bl_label="Save + Export All"
    def execute(self,context):
        out=context.scene.naris_output_dir
        try:
            if context.scene.naris_auto_lod:
                bpy.ops.naris.generate_lods()
            if context.scene.naris_auto_collision:
                bpy.ops.naris.generate_collisions()
            save_blend(out)
            for eng in ("GODOT","UNITY","UNREAL"):
                export_engine(eng,out)
            write_manifest(out)
            self.report({"INFO"},f"NARIS package exported to {out}")
            return {"FINISHED"}
        except Exception as e:
            traceback.print_exc(); self.report({"ERROR"},str(e)); return {"CANCELLED"}


class NARIS_OT_reset_generated(bpy.types.Operator):
    bl_idname="naris.reset_generated"
    bl_label="Reset Generated Scene"
    bl_options={"REGISTER","UNDO"}
    def execute(self,context):
        clean_scene()
        build_collection_tree()
        self.report({"INFO"},"Generated NARIS scene reset")
        return {"FINISHED"}

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
class NARIS_PT_master(bpy.types.Panel):
    bl_label="NARIS Master Builder"
    bl_idname="NARIS_PT_master"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_category="NARIS"
    def draw(self,context):
        s=context.scene; layout=self.layout
        col=layout.column(align=True)
        col.label(text="CALL OF NARIS — Production Pipeline")
        col.operator("naris.build_master",icon="OUTLINER_COLLECTION")
        row=col.row(align=True)
        row.operator("naris.generate_lods",icon="MOD_DECIM")
        row.operator("naris.generate_collisions",icon="PHYSICS")
        row=col.row(align=True)
        row.operator("naris.validate_scene",icon="CHECKMARK")
        row.operator("naris.write_manifest",icon="FILE_TICK")
        col.separator()
        col.operator("naris.export_all",icon="EXPORT")
        row=col.row(align=True)
        op=row.operator("naris.export_engine",text="Godot"); op.engine="GODOT"
        op=row.operator("naris.export_engine",text="Unity"); op.engine="UNITY"
        op=row.operator("naris.export_engine",text="Unreal"); op.engine="UNREAL"
        col.separator()
        col.operator("naris.reset_generated",icon="TRASH")


class NARIS_PT_settings(bpy.types.Panel):
    bl_label="Build Settings"
    bl_idname="NARIS_PT_settings"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_category="NARIS"
    bl_parent_id="NARIS_PT_master"
    bl_options={"DEFAULT_CLOSED"}
    def draw(self,context):
        s=context.scene; layout=self.layout
        layout.prop(s,"naris_output_dir")
        layout.prop(s,"naris_seed")
        layout.prop(s,"naris_clear_before_build")
        layout.prop(s,"naris_auto_lod")
        layout.prop(s,"naris_auto_collision")
        layout.label(text=s.naris_validation_summary)


class NARIS_PT_asset_status(bpy.types.Panel):
    bl_label="Asset Status"
    bl_idname="NARIS_PT_asset_status"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_category="NARIS"
    bl_parent_id="NARIS_PT_master"
    bl_options={"DEFAULT_CLOSED"}
    def draw(self,context):
        layout=self.layout
        assets=[o for o in context.scene.objects if o.get("naris_asset")]
        layout.label(text=f"Registered assets: {len(assets)}")
        for obj in assets[:12]:
            layout.label(text=f"• {obj.get('naris_asset')} [{obj.get('naris_type','ASSET')}]")
        if len(assets)>12:
            layout.label(text=f"… +{len(assets)-12} more")

# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------
CLASSES=(
    NARIS_OT_build_master,
    NARIS_OT_generate_lods,
    NARIS_OT_generate_collisions,
    NARIS_OT_validate,
    NARIS_OT_manifest,
    NARIS_OT_export_engine,
    NARIS_OT_export_all,
    NARIS_OT_reset_generated,
    NARIS_PT_master,
    NARIS_PT_settings,
    NARIS_PT_asset_status,
)


def register_props():
    bpy.types.Scene.naris_output_dir=StringProperty(name="Output",subtype="DIR_PATH",default=DEFAULT_OUTPUT)
    bpy.types.Scene.naris_seed=IntProperty(name="World Seed",default=1337,min=0,max=99999999)
    bpy.types.Scene.naris_clear_before_build=BoolProperty(name="Clear before build",default=True)
    bpy.types.Scene.naris_auto_lod=BoolProperty(name="Generate LODs on Export All",default=True)
    bpy.types.Scene.naris_auto_collision=BoolProperty(name="Generate Collision on Export All",default=True)
    bpy.types.Scene.naris_validation_summary=StringProperty(name="Validation",default="Not validated")


def unregister_props():
    for name in (
        "naris_output_dir","naris_seed","naris_clear_before_build",
        "naris_auto_lod","naris_auto_collision","naris_validation_summary",
    ):
        if hasattr(bpy.types.Scene,name): delattr(bpy.types.Scene,name)


def register():
    # Safe re-register during Scripting iteration.
    for cls in CLASSES:
        try: bpy.utils.register_class(cls)
        except RuntimeError: pass
    register_props()
    log(f"Registered v{ADDON_VERSION}")


def unregister():
    unregister_props()
    for cls in reversed(CLASSES):
        try: bpy.utils.unregister_class(cls)
        except Exception: pass
    log("Unregistered")


if __name__ == "__main__":
    try:
        unregister()
    except Exception:
        pass
    register()
    log("Ready. Open View3D > Sidebar (N) > NARIS, then click Build NARIS Master Scene.")

# v1.1 repository contract notes:
# - W04_AshenForest_environment_factory_v2.json owns grid_m, modular floor/wall height,
#   streaming cell policy and material_slots_max_per_mesh.
# - MASTER_ASSET_REGISTRY.json owns immutable identity/status.
# - W04_ProductionAssetBindings.json owns expected_unreal_object_path and technical gates.
# - naris_export.py remains the registry-gated FBX/GLB exchange path into Unreal.
