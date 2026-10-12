# CALL OF NARIS — P0-BOSS-04 Integration Discovery
# Read-only Unreal Editor inspection. Does NOT modify or save the gameplay map.
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
REPORT=PROJECT_ROOT/"Reports"/"P0-BOSS-04_integration_discovery.json"
MAP_CANDIDATES=[
    "/Game/NARIS/Maps/L_AshMap_Assembly",
    "/Game/NARIS/W04/Maps/W04_AshenForest",
    "/Game/NARIS/W04/Maps/W04_Prototype",
]
MATCH_WORDS=("ashwarden","ash_warden","ash warden")
MATCH_TAGS=("AshWarden","NARIS_Boss","Boss")

def sval(v):
    try:return str(v)
    except Exception:return None

def vec(v):
    try:return [float(v.x),float(v.y),float(v.z)]
    except Exception:return None

def fail(reason,extra=None):
    out={"status":"FAIL","read_only":True,"replacement_allowed":False,"reason":reason}
    if extra:out.update(extra)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log_error("NARIS_P0_BOSS_04_DISCOVERY_FAIL "+json.dumps(out,ensure_ascii=False))
    raise RuntimeError(reason)

loaded_map=None
for mp in MAP_CANDIDATES:
    if unreal.EditorAssetLibrary.does_asset_exist(mp):
        try:
            unreal.EditorLoadingAndSavingUtils.load_map(mp)
            loaded_map=mp
            break
        except Exception as exc:
            unreal.log_warning("NARIS_BOSS_DISCOVERY_MAP "+mp+" "+str(exc))
if not loaded_map:
    fail("no_candidate_gameplay_map_found",{"maps":MAP_CANDIDATES})

actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=list(actor_sub.get_all_level_actors())

matches=[]
for actor in actors:
    try: label=actor.get_actor_label()
    except Exception: label=actor.get_name()
    cls=actor.get_class()
    cls_path=cls.get_path_name() if cls else ""
    try: tags=[str(t) for t in actor.get_editor_property("tags")]
    except Exception: tags=[]
    hay=(" ".join([label,actor.get_name(),cls_path]+tags)).lower()
    if not (any(w in hay for w in MATCH_WORDS) or any(t.lower() in [x.lower() for x in tags] for t in MATCH_TAGS)):
        continue

    sk_components=[]
    try:
        sk_components=list(actor.get_components_by_class(unreal.SkeletalMeshComponent))
    except Exception:
        # Character classes normally expose the inherited mesh property even if
        # get_components_by_class differs in a minor UE Python wrapper.
        try:
            c=actor.get_editor_property("mesh")
            if c:sk_components=[c]
        except Exception:pass

    comps=[]
    for comp in sk_components:
        mesh=None
        try:
            mesh=comp.get_skeletal_mesh_asset() if hasattr(comp,"get_skeletal_mesh_asset") else comp.get_editor_property("skeletal_mesh")
        except Exception:pass
        skeleton=None
        if mesh:
            try:skeleton=mesh.get_editor_property("skeleton")
            except Exception:pass
        try: creation=sval(comp.get_editor_property("creation_method"))
        except Exception: creation=None
        try: anim_mode=sval(comp.get_editor_property("animation_mode"))
        except Exception: anim_mode=None
        try: anim_class=comp.get_editor_property("anim_class")
        except Exception: anim_class=None
        comps.append({
            "component":comp.get_path_name(),
            "creation_method":creation,
            "skeletal_mesh":mesh.get_path_name() if mesh else None,
            "skeleton":skeleton.get_path_name() if skeleton else None,
            "animation_mode":anim_mode,
            "anim_class":anim_class.get_path_name() if anim_class else None,
        })

    matches.append({
        "label":label,
        "name":actor.get_name(),
        "actor_path":actor.get_path_name(),
        "class":cls_path,
        "tags":tags,
        "location":vec(actor.get_actor_location()),
        "rotation":sval(actor.get_actor_rotation()),
        "scale":vec(actor.get_actor_scale3d()),
        "skeletal_components":comps,
    })

if not matches:
    fail("ash_warden_actor_not_found",{
        "map":loaded_map,
        "actor_count":len(actors),
        "search_words":MATCH_WORDS,
        "search_tags":MATCH_TAGS
    })

# Prefer an explicit AshWarden class/label over generic Boss-tag actors.
def rank(item):
    h=(item["label"]+" "+item["name"]+" "+item["class"]).lower()
    score=0
    if "ashwarden" in h or "ash_warden" in h:score+=100
    if "narisashwarden" in h:score+=60
    if "boss" in " ".join(item["tags"]).lower():score+=10
    if item["skeletal_components"]:score+=20
    return score
matches.sort(key=rank,reverse=True)
target=matches[0]

proxy_meshes=[
    c["skeletal_mesh"] for c in target["skeletal_components"]
    if c.get("skeletal_mesh")
]
proxy_confirmed=any("bonebeast" in p.lower() or "bone_beast" in p.lower() for p in proxy_meshes)

native_component=any(
    "native" in str(c.get("creation_method","")).lower()
    for c in target["skeletal_components"]
)

if native_component:
    recommendation="VERIFY_LOCAL_CXX_DEFAULT_OR_BEGINPLAY_BEFORE_OVERRIDE"
elif target["skeletal_components"]:
    recommendation="INSTANCE_OR_BLUEPRINT_COMPONENT_OVERRIDE_MAY_BE_SAFE_AFTER_BACKUP"
else:
    recommendation="NO_SKELETAL_COMPONENT_FOUND_REQUIRES_CLASS_LEVEL_INSPECTION"

result={
    "status":"PASS",
    "read_only":True,
    "replacement_allowed":False,
    "map":loaded_map,
    "actor_count":len(actors),
    "match_count":len(matches),
    "target":target,
    "all_matches":matches,
    "current_proxy_meshes":proxy_meshes,
    "bonebeast_proxy_confirmed":proxy_confirmed,
    "native_skeletal_component":native_component,
    "recommended_integration_strategy":recommendation,
    "next_gate":"Inspect local NarisAshWarden C++/Blueprint ownership using this evidence, then author a reversible P0-BOSS-04 promotion and packaged boss regression. Do not rename or overwrite the proxy blindly."
}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_BOSS_04_DISCOVERY="+json.dumps(result,ensure_ascii=False))
