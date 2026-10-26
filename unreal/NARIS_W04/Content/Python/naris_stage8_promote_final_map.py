"""Author the Stage 8 Ashen Forest production-map shell inside Unreal Editor.
This does not claim final art; it promotes only after required production assets resolve.
"""
import unreal
FINAL="/Game/NARIS/W04/Maps/W04_AshenForest"
BLOCKOUT="/Game/NARIS/W04/Maps/W04_AshenForest_Blockout"
eal=unreal.EditorAssetLibrary
if not eal.does_asset_exist(BLOCKOUT):
    raise RuntimeError("Stage8 blocked: production blockout missing: "+BLOCKOUT)
if eal.does_asset_exist(FINAL):
    unreal.log("[NARIS] Final map already exists; leaving it untouched.")
else:
    ok=eal.duplicate_asset(BLOCKOUT,FINAL)
    if not ok: raise RuntimeError("Could not duplicate production blockout to final-map candidate.")
    unreal.log_warning("[NARIS] W04_AshenForest created as a CANDIDATE. It must pass shipping validator and contain no DEV_/BLOCKOUT_/RuntimeSmokeDirector actors.")
