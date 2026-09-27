import unreal, os
level='/Game/World/Maps/L_AshenForest_VerticalSlice'
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ok=sub.load_level(level)
actors=unreal.EditorLevelLibrary.get_all_level_actors()
lines=[f'LOAD={ok}',f'COUNT={len(actors)}']
for a in actors:
    c=a.get_class().get_name()
    n=a.get_name()
    loc=a.get_actor_location()
    if any(k in c.lower() for k in ['playerstart','light','sky','camera','postprocess','fog','landscape','staticmesh']):
        lines.append(f'{c}|{n}|{loc.x:.1f},{loc.y:.1f},{loc.z:.1f}')
ws=unreal.EditorLevelLibrary.get_editor_world().get_world_settings()
lines.append('WORLDSETTINGS='+str(ws))
out=os.path.join(unreal.Paths.project_saved_dir(),'Diagnostics','map_runtime_dump.txt')
os.makedirs(os.path.dirname(out),exist_ok=True)
open(out,'w',encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
