import bpy
names=["00_GROUND","01_ENVIRONMENT","02_PROPS","03_CHARACTERS_PRODUCTION","04_CREATURES_PRODUCTION","05_WEAPONS","06_VFX","07_AI_MARKERS","99_PROTOTYPE_REFERENCE"]
for n in names:
    if not bpy.data.collections.get(n):
        c=bpy.data.collections.new(n); bpy.context.scene.collection.children.link(c)
for o in bpy.data.objects:
    n=o.name.lower()
    if any(k in n for k in ["rigged_v01","prototype","blockout"]):
        o["naris_status"]="PROTOTYPE_REFERENCE_ONLY"; o.hide_render=True
bpy.context.scene["naris_stage"]="STAGE7_PRODUCTION_ASSEMBLY"
bpy.context.scene["advanced_rig_targets"]="Ash92|Hound82|Demon106|Serpent78|Dragon146"
bpy.context.scene["production_ready"]=False
print("[NARIS] Stage7 production structure installed.")
