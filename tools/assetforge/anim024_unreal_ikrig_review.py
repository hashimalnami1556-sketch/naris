"""UE 5.7 editor-only NON-SHIPPING IK Rig creation, strict opt-in.

Requires imported SkeletalMesh with exact pinned source skeleton.
No existing assets replaced; no production retargeter or solver generated.
Invoke in UE Python only with explicit --apply and NARIS_ANIM024_APPROVE_REVIEW=1.
"""
import argparse, json, os
from pathlib import Path
from anim024_ik_chain_contract import PARENT, CHAINS, PINS

ASSET='/Game/NARIS/Generated/Review/ANIM024/IK_NARIS_18J_REVIEW'

def require_plan(plan):
    if plan.get('id')!='ANIM-024-IK-SOURCE-REVIEW' or plan.get('source_sha256')!=PINS:
        raise ValueError('Source SHA256 or review plan not recognized')
    if plan.get('retarget_root')!='pelvis' or plan.get('joint_count')!=18:
        raise ValueError('Unexpected source skeleton/root')
    if set(plan.get('chains',{}))!=set(CHAINS):
        raise ValueError('Unexpected chain set')
    for n,(a,b) in CHAINS.items():
        c=plan['chains'][n]
        if c.get('start')!=a or c.get('end')!=b:
            raise ValueError(f'Changed source retarget chain: {n}')
    if plan.get('release_ready') is not False:
        raise ValueError('Only non-shipping review plans allowed')

def check_imported_mesh(modifier):
    names={str(n) for n in modifier.get_all_bone_names()}
    if names!=set(PARENT):
        raise ValueError(f'Imported bone mismatch: missing={set(PARENT)-names} extra={names-set(PARENT)}')
    for bone,parent in PARENT.items():
        actual=str(modifier.get_parent_name(bone))
        if actual in ('None','NAME_None',''):actual=None
        if actual!=parent:raise ValueError(f'Imported {bone} parent mismatch: {actual} vs {parent}')
    return True

def dry_run(plan,mesh_path):
    require_plan(plan)
    if not isinstance(mesh_path,str) or not mesh_path.startswith('/Game/') or '..' in mesh_path:
        raise ValueError('Provide exact imported SkeletalMesh asset path')
    return {'status':'DRY_RUN_NO_UE_WRITE','mesh_path_unverified':mesh_path,
            'new_review_path':ASSET,'retarget_root':'pelvis',
            'chains':list(CHAINS),'created':False,'production_ready':False}

def apply(plan,mesh_path,u=None):
    result=dry_run(plan,mesh_path)
    if os.environ.get('NARIS_ANIM024_APPROVE_REVIEW')!='1':
        raise PermissionError('Explicit opt-in env NARIS_ANIM024_APPROVE_REVIEW=1 required')
    if u is None:
        import unreal as u  # Only available inside Unreal Editor Python
    if not str(u.SystemLibrary.get_engine_version()).startswith('5.7'):
        raise RuntimeError('Unreal 5.7 is required')
    if u.EditorAssetLibrary.does_asset_exist(ASSET):
        raise FileExistsError('Will not overwrite existing IK Rig review asset')
    mesh=u.load_asset(mesh_path)
    if mesh is None or not isinstance(mesh,u.SkeletalMesh):
        raise ValueError('Imported SkeletalMesh missing')
    # SkeletonModifier only reads data here; NEVER commit_skeleton_to_skeletal_mesh.
    modifier=u.SkeletonModifier()
    if not modifier.set_skeletal_mesh(mesh):
        raise RuntimeError('Cannot read imported bone tree (plugin may be unavailable)')
    check_imported_mesh(modifier)
    folder,name=ASSET.rsplit('/',1)
    if not u.EditorAssetLibrary.does_directory_exist(folder):
        if not u.EditorAssetLibrary.make_directory(folder):
            raise RuntimeError('Failed to create isolated review asset folder')
    asset=u.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name=name,package_path=folder,
        asset_class=u.IKRigDefinition,factory=u.IKRigDefinitionFactory())
    if asset is None:raise RuntimeError('Review IK Rig factory failed')
    ctl=u.IKRigController.get_controller(asset)
    if ctl is None or not ctl.set_skeletal_mesh(mesh):
        raise RuntimeError('IKRigController mesh assignment failed; asset UNSAVED')
    if not ctl.set_retarget_root('pelvis'):
        raise RuntimeError('Failed to set pelvis as retarget root; asset UNSAVED')
    for chain,(start,end) in CHAINS.items():
        made=str(ctl.add_retarget_chain(chain,start,end,u.Name('None')))
        if made!=chain:raise RuntimeError(f'Unexpected chain {chain}->{made}; asset UNSAVED')
    if str(ctl.get_retarget_root())!='pelvis' or len(ctl.get_retarget_chains())!=7:
        raise RuntimeError('IKRigController postcheck failed; asset UNSAVED')
    for name,(start,end) in CHAINS.items():
        if str(ctl.get_retarget_chain_start_bone(name))!=start or str(ctl.get_retarget_chain_end_bone(name))!=end:
            raise RuntimeError(f'Source chain postcheck failed {name}; asset UNSAVED')
    if not u.EditorAssetLibrary.save_loaded_asset(asset):
        raise RuntimeError('Review asset save failed')
    return {**result,'status':'NEW_REVIEW_SOURCE_IKRIG_CREATED',
            'created':True,'target_rig':'NOT_CREATED','retargeter':'NOT_CREATED'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--mesh-asset',required=True)
    p.add_argument('--apply',action='store_true')
    a=p.parse_args()
    plan=json.loads(a.plan.read_text())
    r=apply(plan,a.mesh_asset) if a.apply else dry_run(plan,a.mesh_asset)
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
