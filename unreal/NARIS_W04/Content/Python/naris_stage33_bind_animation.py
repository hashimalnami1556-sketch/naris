"""NARIS Stage33 production animation binder.
Binds the hero AnimBP class when the production assets exist and validates required
montages. It never fabricates animation content.
"""
import json
from pathlib import Path
import unreal

ROOT="/Game/NARIS/W04"
HERO_BP=ROOT+"/Characters/Hero/BP_NarisHero"
ANIM_BP=ROOT+"/Characters/Hero/Animations/ABP_NarisHero"
MONTAGES=[
 ROOT+"/Characters/Hero/Animations/AM_Hero_LightAttack",
 ROOT+"/Characters/Hero/Animations/AM_Hero_HeavyAttack",
 ROOT+"/Characters/Hero/Animations/AM_Hero_Dodge",
 ROOT+"/Characters/Hero/Animations/AM_Hero_Parry",
]
errors=[]
bound=[]

def asset(path):
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        errors.append("missing:"+path); return None
    return unreal.load_asset(path)

hero=asset(HERO_BP)
abp=asset(ANIM_BP)
for p in MONTAGES:
    a=asset(p)
    if a and not isinstance(a, unreal.AnimMontage):
        errors.append("not_montage:"+p)

if hero and abp:
    try:
        generated=abp.generated_class()
        cdo=unreal.get_default_object(hero.generated_class())
        mesh=cdo.get_editor_property("mesh")
        mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
        mesh.set_editor_property("anim_class", generated)
        unreal.EditorAssetLibrary.save_asset(HERO_BP, only_if_is_dirty=False)
        bound.append("hero_anim_class")
    except Exception as exc:
        errors.append("hero_anim_bind:"+str(exc))

report={"schema":"naris.stage33.animation-bind.v1","bound":bound,"errors":errors,"pass":not errors}
out=Path(unreal.Paths.project_saved_dir())/"TestReports"
out.mkdir(parents=True,exist_ok=True)
(out/"naris_stage33_animation_bind.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
unreal.log("NARIS_STAGE33_ANIMATION_BIND="+json.dumps(report))
if errors: raise RuntimeError("Stage33 animation binding incomplete")
