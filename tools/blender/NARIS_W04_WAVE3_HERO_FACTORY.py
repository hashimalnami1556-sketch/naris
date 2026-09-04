import bpy
import math
from mathutils import Vector

"""CALL OF NARIS — W04 Ashen Forest / Wave 3
Procedural blockout factory for hero locations and underground spaces.
This creates clean source geometry for subsequent art passes; it does not pretend to be final sculpted art.
"""

GRID = 2.0
COLLECTION = "NARIS_W04_WAVE3"

def get_collection():
    c = bpy.data.collections.get(COLLECTION)
    if not c:
        c = bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(c)
    return c

def move_to_collection(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    get_collection().objects.link(obj)

def box(name, size, location=(0,0,0), bevel=0.12):
    bpy.ops.mesh.primitive_cube_add(location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = o.modifiers.new("ControlledBevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    move_to_collection(o)
    return o

def arch(name, width=6.0, height=6.0, depth=1.0):
    # Two pillars plus a lintel; deliberately modular and grid-friendly.
    box(name+"_Pillar_L", (1.0, depth, height), (-width/2+0.5, 0, height/2))
    box(name+"_Pillar_R", (1.0, depth, height), ( width/2-0.5, 0, height/2))
    box(name+"_Lintel", (width, depth, 1.0), (0, 0, height-0.5))

def ring(name, radius=12.0, count=12, height=3.0):
    for i in range(count):
        a = (math.tau/count)*i
        x, y = math.cos(a)*radius, math.sin(a)*radius
        box(f"{name}_{i:02d}", (1.5, 2.0, height), (x, y, height/2), bevel=0.08)
        bpy.context.object.rotation_euler.z = a

def create_waystone(location):
    x,y,z = location
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.9, radius2=0.55, depth=2.8, location=(x,y,z+1.4))
    o=bpy.context.object; o.name="Waystone_Hero"; move_to_collection(o)

def create_rune_marker(location, scale=1.0):
    x,y,z=location
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.45*scale, depth=0.12, location=(x,y,z+0.06))
    o=bpy.context.object; o.name="Naris_Rune_Marker"; move_to_collection(o)

def build():
    # Clean only this factory collection.
    c=get_collection()
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    # Outer ring / watchtower footprint
    ring("OuterRing_Ruin", radius=16, count=16, height=2.8)
    create_waystone((0,0,0))

    # Buried temple: stepped chamber + sanctum arch
    for i in range(4):
        s=24-i*4
        box(f"Temple_Step_{i}",(s,s,0.8),(0,0,i*0.8+0.4))
    arch("Temple_Sanctum_Arch", width=8, height=8, depth=2)

    # Ritual arena: circular readable combat space
    ring("Ritual_Arena_Ring", radius=18, count=16, height=3.2)
    for i in range(4):
        a=math.tau*i/4
        create_rune_marker((math.cos(a)*11, math.sin(a)*11, 0), 1.4)

    # Ash Gate interior
    box("AshGate_Left", (2,10,9), (-6,0,4.5))
    box("AshGate_Right", (2,10,9), (6,0,4.5))
    box("AshGate_Header", (14,10,2), (0,0,9))

    # Underground chamber stack
    for i in range(3):
        z=-3.0*i
        box(f"Undercrypt_Platform_{i}",(28-2*i,22-2*i,0.6),(0,0,z))
    arch("Undercrypt_Arch", width=7, height=5, depth=1.5)

    # Rootbound tunnel guide pieces
    for i in range(8):
        x=i*4-14
        box(f"Tunnel_Rib_{i:02d}",(1.0,8.0,5.0),(x,0,2.5),bevel=0.06)

    # Watchtower vertical stack
    for i in range(6):
        box(f"Watchtower_Level_{i}",(10,10,0.8),(0,0,i*4+0.4))
    arch("Watchtower_Entrance", width=4, height=5, depth=1.5)

    # Den + reliquary sockets
    box("BoneDen_Core",(18,14,1),(0,0,0.5))
    box("Reliquary_Chamber",(8,8,1),(0,0,0.5))
    create_rune_marker((0,0,1))

    print("NARIS W04 Wave 3 hero blockout generated:", len(get_collection().objects), "objects")

if __name__ == "__main__":
    build()
