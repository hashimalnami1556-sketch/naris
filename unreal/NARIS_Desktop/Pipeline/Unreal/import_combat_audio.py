import unreal, os
ROOT=r"C:\Users\Admin\NARIS\SourceAssets\Audio"
DEST="/Game/Audio/SFX"
MAP={
 "SFX_Attack_Whoosh":"whoosh_03.wav",
 "SFX_Hit_Impact":"impact_05.wav",
 "SFX_Parry":"chime_07.wav",
 "SFX_Dodge":"whoosh_07.wav",
 "SFX_Pickup":"coin_05.wav",
 "SFX_QuestComplete":"powerup_09.wav",
 "SFX_BossPhase":"rumble_09.wav",
 "SFX_Save":"chime_03.wav",
 "SFX_Load":"chime_04.wav"
}
unreal.EditorAssetLibrary.make_directory(DEST)
tools=unreal.AssetToolsHelpers.get_asset_tools()
tasks=[]
for name,fn in MAP.items():
    src=os.path.join(ROOT,fn)
    t=unreal.AssetImportTask()
    t.filename=src
    t.destination_path=DEST
    t.destination_name=name
    t.automated=True
    t.replace_existing=True
    t.save=True
    tasks.append(t)
tools.import_asset_tasks(tasks)
ok=0
for name in MAP:
    p=f"{DEST}/{name}"
    a=unreal.load_asset(p)
    if a:
        ok+=1
        unreal.log(f"NARIS_AUDIO_IMPORT {name} CLASS={a.get_class().get_name()}")
    else:
        unreal.log_error(f"NARIS_AUDIO_IMPORT_MISSING {name}")
unreal.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=False,recursive=True)
unreal.log(f"NARIS_AUDIO_IMPORT_DONE {ok}/{len(MAP)}")
