import unreal
paths=[
"/Niagara/DefaultAssets/Templates/Systems/RadialBurst.RadialBurst",
"/Niagara/DefaultAssets/Templates/Systems/DirectionalBurst.DirectionalBurst",
"/Niagara/DefaultAssets/Templates/Systems/SimpleExplosion.SimpleExplosion"]
for p in paths:
 a=unreal.load_asset(p)
 unreal.log("NARIS_NIAGARA_CHECK "+p+" "+("OK "+a.get_class().get_name() if a else "MISSING"))
unreal.log("NARIS_NIAGARA_CHECK_DONE")