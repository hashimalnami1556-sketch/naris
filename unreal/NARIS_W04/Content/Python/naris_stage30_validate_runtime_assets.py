"""Stage 30 editor validation for animation and PBR production assets.
Run with UnrealEditor-Cmd NARIS_W04.uproject -ExecutePythonScript=... -unattended -NullRHI
"""
import unreal, json, os
ROOT="/Game/NARIS/W04"
required_anim=[
 ROOT+"/Characters/Hero/Animations/ABP_NarisHero",
 ROOT+"/Characters/Hero/Animations/AM_Hero_LightAttack",
 ROOT+"/Characters/Hero/Animations/AM_Hero_HeavyAttack",
 ROOT+"/Characters/Hero/Animations/AM_Hero_Dodge",
]
required_env=[
 ROOT+"/Environment/Materials/M_Ground_Master",
 ROOT+"/Environment/Materials/M_Tree_Master",
 ROOT+"/Environment/Materials/M_Ruins_Master",
]
missing=[]
for p in required_anim+required_env:
    if not unreal.EditorAssetLibrary.does_asset_exist(p):
        missing.append(p)
report={"stage":30,"missing":missing,"animation_required":required_anim,"pbr_required":required_env,"pass":not missing}
unreal.log("[NARIS Stage30] "+json.dumps(report))
if missing:
    raise RuntimeError("Stage30 production assets unresolved: "+", ".join(missing))
