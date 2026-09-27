from pathlib import Path
import shutil
root=Path(r"C:\Users\Admin\NARIS")
backup=Path(r"C:\Users\Admin\NARIS_Backup_20260927")
files=["Source/NarisCore/Private/NarisGameModeBase.cpp","Source/NarisCore/Private/NarisHUD.cpp","Source/NarisCore/Private/NarisCheckpointActor.cpp","Source/NarisCore/Private/NarisSaveSubsystem.cpp"]
for name in files:
 p=backup/name;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): raise RuntimeError("Backup already exists: "+str(p))
 shutil.copy2(root/name,p)
def replace(name,old,new):
 p=root/name;s=p.read_text(encoding="utf-8-sig")
 if s.count(old)!=1: raise RuntimeError("Anchor mismatch: "+name)
 p.write_text(s.replace(old,new),encoding="utf-8")
gm=files[0];cp=files[2];save=files[3]
replace(cp,'#include "NarisWorldStateSubsystem.h"','#include "NarisWorldStateSubsystem.h"\n#include "Misc/CommandLine.h"\n#include "Misc/Parse.h"')
replace(cp,'S->SavePlayer(P,TEXT("NARIS_Auto"))','S->SavePlayer(P,FParse::Param(FCommandLine::Get(),TEXT("NarisQuestSmoke"))?TEXT("NARIS_SmokeCheckpoint"):TEXT("NARIS_Auto"))')
replace(gm,'UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_Auto"),0)','UGameplayStatics::DoesSaveGameExist(TEXT("NARIS_SmokeCheckpoint"),0)')
replace(gm,'UGameplayStatics::DeleteGameInSlot(TEXT("NARIS_Auto"),0)','UGameplayStatics::DeleteGameInSlot(TEXT("NARIS_SmokeCheckpoint"),0)')
replace(save,'P->SetActorTransform(S->PlayerTransform,false,nullptr,ETeleportType::TeleportPhysics);','if(S->SchemaVersion!=GetDefault<UNarisSaveGame>()->SchemaVersion || S->PlayerTransform.ContainsNaN() || !FMath::IsFinite(S->Health) || !FMath::IsFinite(S->Energy)){\n  UE_LOG(LogTemp,Warning,TEXT("NARIS_LOAD REJECTED Slot=%s Schema=%d"),*Slot,S->SchemaVersion);return false;\n }\n P->SetActorTransform(S->PlayerTransform,false,nullptr,ETeleportType::TeleportPhysics);')
print("PATCH_APPLIED: isolated smoke checkpoint slot; validate save before mutating player")
