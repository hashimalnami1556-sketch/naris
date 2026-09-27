import unreal
ROOT="/Game/Art/Characters/RiggedV4"
expected={"AshenVessel":["AN_Ashen_Attack_Heavy","AN_Ashen_Attack_Light","AN_Ashen_Dodge","AN_Ashen_HitReact","AN_Ashen_Idle","AN_Ashen_Parry","AN_Ashen_Resonance","AN_Ashen_Run","AN_Ashen_Walk"],"CelestialWolf":["AN_Wolf_Bite","AN_Wolf_Dash","AN_Wolf_Idle","AN_Wolf_Roar","AN_Wolf_Run","AN_Wolf_SoulVision"],"BoneBeast":["AN_Beast_Enrage","AN_Beast_Idle","AN_Beast_Roar","AN_Beast_Run","AN_Beast_Stunned","AN_Beast_Swipe","AN_Beast_TailSweep"]}
errors=[]
deleted=[]
for char,names in expected.items():
 d=ROOT+"/"+char
 assets=unreal.EditorAssetLibrary.list_assets(d,recursive=False,include_folder=False)
 for n in names:
  exact=d+"/"+n
  if not unreal.EditorAssetLibrary.does_asset_exist(exact):
   errors.append(char+" missing "+n)
   continue
  for p in list(assets):
   pkg=p.split(".")[0]
   leaf=pkg.rsplit("/",1)[-1]
   if pkg!=exact and n.lower() in leaf.lower() and leaf.startswith("SK_"):
    if unreal.EditorAssetLibrary.delete_asset(pkg):
     deleted.append(pkg)
 if not unreal.EditorAssetLibrary.does_asset_exist(d+"/SK_"+char):
  errors.append(char+" missing skeletal mesh")
unreal.log(("NARIS_RIG_V4_VALIDATE_PASS" if not errors else "NARIS_RIG_V4_VALIDATE_FAIL")+" deleted="+str(len(deleted))+" errors="+str(errors))
