"""Stage28 W04 authoring preview. Never overwrite production map or claim playable status."""
import json
from pathlib import Path
import unreal
PROJECT=Path(unreal.Paths.project_dir())
CONTRACT=PROJECT/"Stage28"/"STAGE28_W04_AUTHORING_CONTRACT.json"
REPORT=Path(unreal.Paths.project_saved_dir())/"TestReports"/"naris_stage28_authoring.json"
PREVIEW_MAP="/Game/NARIS/_Import/Stage28_W04/W04_AshenForest_AuthoringPreview"
def spawn(cls,label,xyz):
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(cls,unreal.Vector(*xyz))
    if not a:raise RuntimeError("Failed to spawn "+label)
    a.set_actor_label(label)
    return a
def main():
    result={"schema":"naris.stage28.unreal-authoring.v1","status":"fail","preview_map":PREVIEW_MAP,"created_labels":[],"production_map_promoted":False,"errors":[]}
    try:
        c=json.loads(CONTRACT.read_text(encoding="utf-8"))
        if unreal.EditorAssetLibrary.does_asset_exist(PREVIEW_MAP):
            raise RuntimeError("Preview already exists: refusing to overwrite")
        if not unreal.EditorLevelLibrary.new_level(PREVIEW_MAP):
            raise RuntimeError("Cannot create preview level")
        for zone in c["zones"]:
            x,y=zone["xy_cm"]
            label="ZONE_"+zone["id"]
            spawn(unreal.TargetPoint,label,(x,y,100))
            result["created_labels"].append(label)
        markers={"PlayerStart":(0,0,150),"NARIS_Waystone_0001":(1500,0,100),"NARIS_MemoryCrystal_0001":(18500,0,100),"NARIS_AshGate_0001":(68000,0,100),"NARIS_CelestialWolf_0001":(52000,0,100),"NARIS_BoneBeastBoss_0001":(85000,0,100),"NARIS_BossArenaController":(86000,0,100)}
        for label,xyz in markers.items():
            spawn(unreal.PlayerStart if label=="PlayerStart" else unreal.TargetPoint,label,xyz)
            result["created_labels"].append(label)
        spawn(unreal.DirectionalLight,"W04_Dusk_Key",(0,0,4000))
        spawn(unreal.SkyLight,"W04_SkyFill",(0,0,2000))
        spawn(unreal.ExponentialHeightFog,"W04_Mist",(0,0,0))
        nav=spawn(unreal.NavMeshBoundsVolume,"W04_NavMesh_Bounds",(42500,0,0))
        nav.set_actor_scale3d(unreal.Vector(900,160,30))
        if not unreal.EditorLevelLibrary.save_current_level():
            raise RuntimeError("Failed to save preview")
        result["status"]="preview_markers_created_not_playable"
        result["warnings"]=["Import GLB geometry separately","TargetPoint markers are NOT gameplay actors","Collision NavMesh AI and PIE remain untested","Do not promote preview to production map"]
    except Exception as exc:result["errors"].append(str(exc))
    finally:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(result,indent=2),encoding="utf-8")
        unreal.log("NARIS_STAGE28="+json.dumps(result))
    if result["errors"]:raise RuntimeError("; ".join(result["errors"]))
if __name__=="__main__":main()
