import unreal
paths=[
"/Game/Art/Characters/Rigged/SK_AshenVessel",
"/Game/Art/Characters/Rigged/SK_CelestialWolf",
"/Game/Art/Characters/Rigged/SK_BoneBeast",
"/Game/Art/Characters/Rigged/AN_Ashen_Idle",
"/Game/Art/Characters/Rigged/AN_Wolf_Idle",
"/Game/Art/Characters/Rigged/AN_Beast_Idle"]
for p in paths:
    a=unreal.load_asset(p)
    if not a:
        unreal.log_error("RIG_INSPECT_MISSING "+p)
        continue
    cls=a.get_class().get_name()
    sk=""
    try:
        s=a.get_editor_property("skeleton")
        if s: sk=s.get_path_name()
    except Exception:
        pass
    unreal.log("RIG_INSPECT "+p+" CLASS="+cls+" SKELETON="+sk)
unreal.log("RIG_INSPECT_DONE")