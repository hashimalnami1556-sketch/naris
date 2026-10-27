"""UE editor read-only compatibility report for skeletal meshes, sequences and montages."""
import json
from pathlib import Path
import unreal

def main():
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    data = reg.get_assets_by_path(unreal.Name('/Game/NARIS'), recursive=True)
    rows = []
    for entry in data:
        kind = str(entry.asset_class_path.asset_name)
        if kind not in ('SkeletalMesh','AnimSequence','AnimMontage','AnimBlueprint'):
            continue
        path = str(entry.package_name)
        asset = unreal.EditorAssetLibrary.load_asset(path)
        skeleton_path = None
        if asset:
            try:
                skeleton = asset.get_editor_property('skeleton')
                skeleton_path = skeleton.get_path_name() if skeleton else None
            except Exception:
                pass
        rows.append({'path':path,'class':kind,'skeleton':skeleton_path})
    skeletons = {r['skeleton'] for r in rows if r['class']=='SkeletalMesh' and r['skeleton']}
    missing = [r['path'] for r in rows if r['class'] in ('AnimSequence','AnimMontage')
               and (not r['skeleton'] or r['skeleton'] not in skeletons)]
    report = {'stage':37,'assets':rows,'skeletons_with_mesh':sorted(skeletons),
              'animation_without_matching_mesh_skeleton':missing,
              'note':'Asset linkage audit only; not animation playback, retarget or PIE test.'}
    output = Path(unreal.Paths.project_saved_dir())/'TestReports'/'naris_stage37_animation_links.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    unreal.log('Stage37 report: '+str(output))
    if missing: unreal.log_warning('Stage37 unmatched animations: '+str(len(missing)))

if __name__=='__main__':main()
