"""Import audited owner GLBs into an isolated editor review map; never promote art."""
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[4]
MANIFEST = ROOT / 'data/intake/w04-20261011.json'
DESTINATION = '/Game/NARIS/Intake/W04_20261011'


def import_candidate(entry):
    source = (ROOT / entry['source']).resolve()
    if ROOT not in source.parents or source.suffix != '.glb':
        raise RuntimeError('Invalid source path')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != entry['audit']['sha256'] or entry['audit']['geometry_validation'] != 'pass':
        raise RuntimeError('Source differs from audited geometry: ' + entry['slug'])
    destination = DESTINATION + '/' + entry['slug'].replace('-', '_')
    existing = unreal.EditorAssetLibrary.list_assets(destination, recursive=True, include_folder=False)
    objects = [unreal.load_asset(p) for p in existing]
    meshes = [o for o in objects if isinstance(o, (unreal.StaticMesh, unreal.SkeletalMesh))]
    if meshes:
        if any(unreal.EditorAssetLibrary.get_metadata_tag(m, 'NARIS.SourceSHA256') != digest for m in meshes):
            raise RuntimeError('Existing intake geometry has different provenance; use a new batch')
    else:
        if existing:
            raise RuntimeError('Partial previous import; inspect destination before retry')
        task = unreal.AssetImportTask()
        for key, value in {'filename':str(source),'destination_path':destination,
                'automated':True,'replace_existing':False,'replace_existing_settings':False,
                'save':True,'async_':False}.items():
            task.set_editor_property(key, value)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        objects = list(task.get_objects())
        meshes = [o for o in objects if isinstance(o, (unreal.StaticMesh, unreal.SkeletalMesh))]
        if not meshes:
            raise RuntimeError('No mesh imported. Enable the UE glTF Interchange importer and inspect the log.')
        for obj in objects:
            for key, value in {'NARIS.AssetId':entry['asset_id'], 'NARIS.SourceSHA256':digest,
                'NARIS.Stage':'source_candidate', 'NARIS.ProductionApproved':'false'}.items():
                unreal.EditorAssetLibrary.set_metadata_tag(obj, key, value)
        if not unreal.EditorAssetLibrary.save_directory(destination, only_if_is_dirty=False, recursive=True):
            raise RuntimeError('Failed to save ' + destination)
    if len(meshes) != 1:
        raise RuntimeError('Expected a single display mesh per GLB; inspect imported scene')
    if bool(entry['audit']['joint_counts']) != isinstance(meshes[0], unreal.SkeletalMesh):
        raise RuntimeError('Importer changed static/skeletal type: ' + entry['slug'])
    return meshes[0]


def spawn(actor_subsystem, cls, label, location):
    actor = actor_subsystem.spawn_actor_from_class(cls, unreal.Vector(*location), transient=False)
    if not actor: raise RuntimeError('Cannot spawn ' + label)
    actor.set_actor_label(label)
    return actor


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    registry = json.loads((ROOT / 'data/MASTER_ASSET_REGISTRY.json').read_text(encoding='utf-8'))
    ids = [a['id'] for a in registry['assets']]
    for entry in manifest['assets']:
        if ids.count(entry['asset_id']) != 1:
            raise RuntimeError('Unregistered/ambiguous candidate ' + entry['asset_id'])
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    map_path = manifest['map']
    # Import into quarantine first. Never touch the production map or default startup settings.
    imported = [(entry, import_candidate(entry)) for entry in manifest['assets']]
    if unreal.EditorAssetLibrary.does_asset_exist(map_path):
        if not level.load_level(map_path): raise RuntimeError('Cannot load review map')
        if not level.save_current_level(): raise RuntimeError('Cannot save review map')
        unreal.log('NARIS_INTAKE_REVIEW existing map loaded; placements preserved')
        return
    if not level.new_level(map_path, False): raise RuntimeError('Cannot create review map')
    floor = spawn(actors, unreal.StaticMeshActor, 'DEV_IntakeWalkway', (8000, 0, -50))
    floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube.Cube'))
    floor.set_actor_scale3d(unreal.Vector(200, 45, 1))
    placements = []
    for i, (entry, mesh) in enumerate(imported):
        location = [i*4000, 0, 0]
        if isinstance(mesh, unreal.SkeletalMesh):
            actor = spawn(actors, unreal.SkeletalMeshActor, 'DEV_' + entry['slug'], location)
            component = actor.get_editor_property('skeletal_mesh_component')
            component.set_skeletal_mesh_asset(mesh)
            # No inferred retargeting, Animation Blueprint or combat bindings.
        else:
            actor = spawn(actors, unreal.StaticMeshActor, 'DEV_' + entry['slug'], location)
            component = actor.get_editor_property('static_mesh_component')
            component.set_static_mesh(mesh)
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        origin, extent = actor.get_actor_bounds(False)
        dimension = extent.z*2 if entry['asset_id'].split('-')[2] == 'CHR' else max(extent.x,extent.y,extent.z)*2
        if dimension <= 0: raise RuntimeError('Zero imported bounds')
        scale = entry['display_height_cm'] / dimension
        actor.set_actor_scale3d(unreal.Vector(scale,scale,scale))
        origin, extent = actor.get_actor_bounds(False)
        # Imported pivot and glTF -> Unreal conversion are measured rather than assumed.
        current = actor.get_actor_location()
        actor.set_actor_location(unreal.Vector(current.x + location[0] - origin.x,
            current.y - origin.y, current.z + extent.z - origin.z), False, False)
        placements.append({'asset_id':entry['asset_id'],'mesh':mesh.get_path_name(),'scale':scale})
    spawn(actors, unreal.PlayerStart, 'DEV_IntakePlayerStart', (-800,-1000,120))
    light=spawn(actors, unreal.DirectionalLight, 'DEV_IntakeSun', (0,0,1000))
    light.set_actor_rotation(unreal.Rotator(-45,-30,0), False)
    spawn(actors, unreal.SkyLight, 'DEV_IntakeSky', (0,0,900))
    if not level.save_current_level(): raise RuntimeError('Cannot save review level')
    report_dir = Path(unreal.Paths.project_saved_dir()) / 'NARIS/Intake'; report_dir.mkdir(parents=True,exist_ok=True)
    report = {'map':map_path,'status':'imported_review_only','placements':placements,
        'production_approved':False,'playtest':'not_run'}
    (report_dir / 'w04-20261011-import.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    unreal.log('NARIS_INTAKE_RESULT=' + json.dumps(report))


if __name__ == '__main__': main()
