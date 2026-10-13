# CALL OF NARIS — P0-05 Hero Rollback
# Transactional recovery rule: ACTIVE must never be left empty.
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
REPORT=PROJECT_ROOT/"Reports"/"P0-05_rollback.json"
ACTIVE="/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3"
ARCHIVE="/Game/NARIS/Characters/HeroV3/Archive/SK_NARIS_AshenVessel_v3_PreP0"
CANDIDATE="/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production"
TEMP_NEW="/Game/NARIS/Characters/HeroProduction/RollbackTemp/SK_NARIS_AshenVessel_Promoted"

def exists(path):
    return unreal.EditorAssetLibrary.does_asset_exist(path)

def write_result(result):
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log("NARIS_P0_05_ROLLBACK="+json.dumps(result,ensure_ascii=False))

result={"status":"FAIL","rolled_back":False,"active_preserved":False}

if not exists(ARCHIVE):
    result["reason"]="archive_missing"
elif not exists(ACTIVE):
    # The safest recovery if ACTIVE disappeared but archive still exists.
    restored=unreal.EditorAssetLibrary.rename_asset(ARCHIVE,ACTIVE)
    result.update({
        "status":"PASS" if restored else "FAIL",
        "rolled_back":restored,
        "active_preserved":restored,
        "reason":"active_missing_restored_from_archive" if restored else "active_missing_and_archive_restore_failed",
        "restored":ACTIVE if restored else None
    })
else:
    # Never move ACTIVE directly to CANDIDATE first. Stage it to a temporary path,
    # restore the known-good archive, then put the promoted candidate back.
    unreal.EditorAssetLibrary.make_directory("/Game/NARIS/Characters/HeroProduction/RollbackTemp")
    if exists(TEMP_NEW):
        result["reason"]="rollback_temp_path_occupied"
    elif exists(CANDIDATE):
        result["reason"]="candidate_original_path_already_occupied"
    else:
        staged=unreal.EditorAssetLibrary.rename_asset(ACTIVE,TEMP_NEW)
        if not staged:
            result["reason"]="failed_to_stage_promoted_active"
            result["active_preserved"]=exists(ACTIVE)
        else:
            restored=unreal.EditorAssetLibrary.rename_asset(ARCHIVE,ACTIVE)
            if not restored:
                # Restore the promoted hero back to ACTIVE so the game remains bootable.
                recovered=unreal.EditorAssetLibrary.rename_asset(TEMP_NEW,ACTIVE)
                result.update({
                    "reason":"archive_restore_failed",
                    "active_preserved":recovered,
                    "recovered_promoted_active":recovered
                })
            else:
                candidate_restored=unreal.EditorAssetLibrary.rename_asset(TEMP_NEW,CANDIDATE)
                result={
                    "status":"PASS",
                    "rolled_back":True,
                    "active_preserved":exists(ACTIVE),
                    "restored":ACTIVE,
                    "candidate":CANDIDATE if candidate_restored else TEMP_NEW,
                    "candidate_restored_to_original_path":candidate_restored,
                    "note":None if candidate_restored else "Working HeroV3 restored; promoted candidate remains safely staged at rollback temp path."
                }

# A rename in the loaded editor is insufficient: recovery must persist to disk.
if result.get("rolled_back"):
    try:
        saved=unreal.EditorAssetLibrary.save_directory("/Game/NARIS/Characters",False,True)
        if not saved:
            raise RuntimeError("save_directory_returned_false")
        result["persisted"]=True
    except Exception as exc:
        result.update({"status":"FAIL","rolled_back":False,"persisted":False,
                       "recovered_in_memory":True,"reason":"rollback_save_failed","save_error":str(exc)})
write_result(result)
if not result.get("rolled_back"):
    raise RuntimeError(result.get("reason","rollback_failed"))
