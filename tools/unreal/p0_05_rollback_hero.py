# CALL OF NARIS — P0-05 Hero Rollback
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
REPORT=PROJECT_ROOT/"Reports"/"P0-05_rollback.json"
ACTIVE="/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3"
ARCHIVE="/Game/NARIS/Characters/HeroV3/Archive/SK_NARIS_AshenVessel_v3_PreP0"
CANDIDATE="/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production"

result={"status":"FAIL","rolled_back":False}
if not unreal.EditorAssetLibrary.does_asset_exist(ARCHIVE):
    result["reason"]="archive_missing"
else:
    if unreal.EditorAssetLibrary.does_asset_exist(CANDIDATE):
        result["reason"]="candidate_original_path_already_occupied"
    elif not unreal.EditorAssetLibrary.does_asset_exist(ACTIVE):
        result["reason"]="promoted_active_missing"
    else:
        moved_new=unreal.EditorAssetLibrary.rename_asset(ACTIVE,CANDIDATE)
        moved_old=unreal.EditorAssetLibrary.rename_asset(ARCHIVE,ACTIVE) if moved_new else False
        if moved_new and moved_old:
            result={"status":"PASS","rolled_back":True,"restored":ACTIVE,"candidate":CANDIDATE}
            unreal.EditorAssetLibrary.save_directory("/Game/NARIS/Characters",False,True)
        else:
            result["reason"]="rename_rollback_failed"
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_05_ROLLBACK="+json.dumps(result,ensure_ascii=False))
if not result.get("rolled_back"):
    raise RuntimeError(result.get("reason","rollback_failed"))
