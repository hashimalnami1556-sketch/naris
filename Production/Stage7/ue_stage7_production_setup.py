import unreal
root="/Game/NARIS"
folders=["Characters/AshWanderer/Production","Characters/DemonWarrior/Production","Creatures/BoneHound/Production","Creatures/AetherSerpent/Production","Creatures/Dragon/Production","Environment/Ground/Production","Environment/Props/Production","Weapons/Production","VFX/Production","AI/Production","Maps/Production","QA/Stage7"]
for f in folders:
    p=f"{root}/{f}"
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)
unreal.log("[NARIS] Stage7 folders ready; runtime gates remain mandatory.")
