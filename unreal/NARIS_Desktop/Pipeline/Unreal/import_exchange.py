import unreal, os
SRC=r"C:\Users\Admin\NARIS\Pipeline\Exchange\FBX"
DEST="/Game/Art/Imported"
unreal.EditorAssetLibrary.make_directory(DEST)
task=unreal.AssetImportTask()
task.automated=True
task.destination_path=DEST
task.replace_existing=True
task.save=True
files=[os.path.join(SRC,f) for f in os.listdir(SRC) if f.lower().endswith('.fbx')] if os.path.isdir(SRC) else []
for f in files:
    t=unreal.AssetImportTask()
    t.filename=f
    t.destination_path=DEST
    t.automated=True
    t.replace_existing=True
    t.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    unreal.log('Imported '+f)
