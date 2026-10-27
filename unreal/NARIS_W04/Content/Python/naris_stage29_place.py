"""Guarded Stage29 G1 authoring. Defaults to read-only preflight.
No animation/GAS migration, final-map promotion or PIE success is implied.
"""
import datetime
import importlib.util
import hashlib
import subprocess
import json
from pathlib import Path
import uuid
import unreal

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stage29_rules', BASE / 'naris_stage29_rules.py')
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)


def xyz(v):
    return [float(v.x), float(v.y), float(v.z)]


def material_paths(mesh):
    prop = 'materials' if isinstance(mesh, unreal.SkeletalMesh) else 'static_materials'
    slots = list(mesh.get_editor_property(prop))
    result = []
    for slot in slots:
        material = slot.get_editor_property('material_interface')
        result.append(material.get_path_name() if material else None)
    return result


def execute(apply=False, template=None):
    project = Path(unreal.Paths.project_dir()).resolve()
    root = project.parents[1]
    source = project / 'Content/NARIS/W04/Production/Stage29'
    data = json.loads((source / 'placements_corrected.json').read_text())
    policy = json.loads((source / 'placement_policy.json').read_text())
    layout = json.loads((root / 'NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json').read_text())
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    static = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    run_id = uuid.uuid4().hex
    report_path = Path(unreal.Paths.project_saved_dir()) / 'TestReports' / ('stage29_g1_' + run_id + '.json')
    try:
        commit = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=5, check=True).stdout.strip()
    except Exception:
        commit = 'unknown'
    report = {'source_commit': commit, 'engine_version': unreal.SystemLibrary.get_engine_version(),
              'manifest_sha256': hashlib.sha256((source/'placements_corrected.json').read_bytes()).hexdigest(),
              'policy_sha256': hashlib.sha256((source/'placement_policy.json').read_bytes()).hexdigest(),
              'layout_sha256': hashlib.sha256((root/'NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json').read_bytes()).hexdigest(),
              'schema': 'naris.stage29.g1.v1', 'run_id': run_id,
              'date_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'engine_executed': True, 'mode': 'apply' if apply else 'dry_run',
              'map_saved': False, 'elements': [], 'errors': [], 'runtime_review': {},
              'attempted': len(data.get('placements', [])), 'map': None,
              'G2': 'NOT_RUN', 'G3': 'NOT_RUN'}
    created = False
    spawned = []
    previous = None
    mesh_by_key = {}
    try:
        report['errors'].extend(rules.validate_manifest(data, layout, policy['roles']))
        if levels.is_in_play_in_editor(): report['errors'].append('Stop PIE first')
        if (unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
                or unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
            report['errors'].append('Save existing editor work before intake')
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        inventory = registry.get_assets_by_path('/Game/NARIS/_Import/Stage28_PBR', recursive=True)
        candidates = [str(a.package_name) + '.' + str(a.asset_name) for a in inventory
                      if str(a.asset_class_path.asset_name) in ('StaticMesh', 'SkeletalMesh')]
        report['resolved_assets'] = {}
        for key in sorted({p['asset_key'] for p in data['placements']}):
            path = rules.resolve_asset(key, candidates, policy.get('asset_path_overrides', {}).get(key))
            if not path:
                report['errors'].append(key + ': missing/ambiguous exact mesh name; set explicit override'); continue
            mesh = unreal.load_asset(path)
            if not isinstance(mesh, (unreal.StaticMesh, unreal.SkeletalMesh)):
                report['errors'].append(key + ': could not load mesh'); continue
            materials = material_paths(mesh)
            if not materials or any(m is None or '/Engine/EngineMaterials/DefaultMaterial' in m for m in materials):
                report['errors'].append(key + ': missing/default material slot')
            collision_ok = True
            collision_evidence = 'decoration: NoCollision intended'
            if policy['roles'][key]['collision'] == 'solid':
                if isinstance(mesh, unreal.StaticMesh):
                    count = static.get_simple_collision_count(mesh)
                    collision_ok = count > 0
                    collision_evidence = 'simple_shape_count=' + str(count)
                else:
                    collision_ok = mesh.get_editor_property('physics_asset') is not None
                    collision_evidence = 'PhysicsAsset assigned=' + str(collision_ok)
                if not collision_ok: report['errors'].append(key + ': authored collision missing')
            report['resolved_assets'][key] = {'path': path, 'materials': materials, 'collision': collision_evidence}
            mesh_by_key[key] = mesh
        env_keys = [k for k,v in policy['roles'].items() if v.get('domain') == 'environment']
        env_materials = {m for k in env_keys for m in report['resolved_assets'].get(k, {}).get('materials', []) if m}
        report['environment_unique_materials'] = len(env_materials)
        report['environment_material_instances'] = sum(isinstance(unreal.load_asset(m), unreal.MaterialInstance) for m in env_materials)
        report['proposed_material_instance_budget'] = policy['environment_material_budget_proposed']
        if report['environment_material_instances'] > policy['environment_material_budget_proposed']:
            report['errors'].append('Environment material-instance budget exceeded')
        if apply:
            if not template or not unreal.EditorAssetLibrary.does_asset_exist(template):
                report['errors'].append('Existing ground-bearing template map is required; no empty-map fallback')
        if report['errors'] or not apply:
            return report
        previous = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split('.')[0]
        target = data['target_map'] + '_' + run_id
        if unreal.EditorAssetLibrary.does_asset_exist(target): raise RuntimeError('Run map already exists')
        if not levels.new_level_from_template(target, template): raise RuntimeError('Template duplication failed')
        created = True
        report['map'] = target
        if any(a.get_actor_label().startswith('ST29_') for a in actors.get_all_level_actors()):
            raise RuntimeError('Template already contains Stage29 actors; choose the ground-only authoring template')
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        # Obtain all ground hits before spawning: no props can become another prop's ground.
        hits = {}
        for p in data['placements']:
            x, y, z = p['transform']['location_cm']
            height = policy['trace_half_height_cm']
            hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, z + height),
                unreal.Vector(x, y, z - height), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                False, [], unreal.DrawDebugTrace.NONE)
            if hit is None: raise RuntimeError(p['id'] + ': no blocking ground hit')
            hits[p['id']] = hit.impact_point
        for p in data['placements']:
            row = {'id': p['id'], 'status': 'failed'}
            report['elements'].append(row)
            t = p['transform']; pitch, yaw, roll = t['rotation_deg']
            actor = actors.spawn_actor_from_object(mesh_by_key[p['asset_key']],
                unreal.Vector(*t['location_cm']), unreal.Rotator(pitch=pitch, yaw=yaw, roll=roll))
            if actor is None: raise RuntimeError(p['id'] + ': spawn failed')
            spawned.append(actor)
            actor.set_actor_label('ST29_' + p['id'])
            actor.set_folder_path('Stage29/' + p['zone'])
            actor.set_actor_scale3d(unreal.Vector(*t['scale']))
            origin, extent = actor.get_actor_bounds(False)
            if extent.z <= 0: raise RuntimeError(p['id'] + ': zero-height bounds')
            loc = actor.get_actor_location()
            loc.z += hits[p['id']].z - (origin.z - extent.z)
            actor.set_actor_location(loc, False, False)
            role = policy['roles'][p['asset_key']]['collision']
            for comp in actor.get_components_by_class(unreal.PrimitiveComponent):
                comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if role == 'solid'
                                           else unreal.CollisionEnabled.NO_COLLISION)
                if role == 'solid': comp.set_collision_profile_name('BlockAll')
            origin, extent = actor.get_actor_bounds(False)
            rot = actor.get_actor_rotation()
            angular_error = lambda a, b: abs((a - b + 180) % 360 - 180)
            row.update(status='placed', asset_path=mesh_by_key[p['asset_key']].get_path_name(),
                location_cm=xyz(actor.get_actor_location()), scale=xyz(actor.get_actor_scale3d()),
                rotation_deg=[rot.pitch, rot.yaw, rot.roll], ground_z_cm=float(hits[p['id']].z),
                ground_ok=abs(origin.z - extent.z - hits[p['id']].z) <= policy['ground_tolerance_cm'],
                materials_assigned=all(material_paths(mesh_by_key[p['asset_key']])),
                collision_ok=all(c.get_collision_enabled() == (unreal.CollisionEnabled.QUERY_AND_PHYSICS if role == 'solid'
                    else unreal.CollisionEnabled.NO_COLLISION) for c in actor.get_components_by_class(unreal.PrimitiveComponent)),
                scale_ok=all(abs(a-b) < 1e-5 for a,b in zip(xyz(actor.get_actor_scale3d()),t['scale'])),
                rotation_ok=all(angular_error(a,b) < .01 for a,b in zip([rot.pitch,rot.yaw,rot.roll],t['rotation_deg'])),
                bounds_ok=(abs(origin.x)+extent.x <= layout['bounds_m']['x']*50
                           and abs(origin.y)+extent.y <= layout['bounds_m']['y']*50))
            if not all(row[k] for k in ('ground_ok','materials_assigned','collision_ok','scale_ok','rotation_ok','bounds_ok')):
                raise RuntimeError(p['id'] + ': measured actor check failed')
        report['map_saved'] = bool(levels.save_current_level())
        if not report['map_saved']: raise RuntimeError('Map save failed')
    except Exception as exc:
        report['errors'].append(str(exc))
        # Only this run's actors/map are eligible for cleanup. Preserve every pre-existing package.
        if created and not report['map_saved']:
            try:
                for actor in spawned: actors.destroy_actor(actor)
                if not previous or not levels.load_level(previous): raise RuntimeError('Cannot restore previous level')
                if not unreal.EditorAssetLibrary.delete_asset(report['map']): raise RuntimeError('Cannot delete new failed copy')
                report['rollback'] = 'new_run_map_removed'
            except Exception as cleanup:
                report['rollback'] = 'quarantined_cleanup_required'
                report['errors'].append('Cleanup: ' + str(cleanup))
    finally:
        report['placed'] = sum(r['status'] == 'placed' for r in report['elements'])
        complete = len(report['elements']) == report['attempted'] and report['placed'] == report['attempted']
        report['measurement_summary'] = {label: sum(r.get(check) is not True for r in report['elements']) if complete else None
            for label,check in [('elements_out_of_bounds','bounds_ok'),('elements_with_missing_materials','materials_assigned'),
                                ('elements_with_invalid_collision','collision_ok'),('z_height_anomalies','ground_ok'),
                                ('scale_anomalies','scale_ok'),('rotation_anomalies','rotation_ok')]}
        report['visibility_in_PIE'] = None
        report['G1'] = rules.decide_g1(report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        unreal.log('Stage29 report: ' + str(report_path) + ' | ' + report['G1']['decision'])
    return report


if __name__ == '__main__':
    execute()  # Explicit execute(apply=True, template=...) required for authoring.
