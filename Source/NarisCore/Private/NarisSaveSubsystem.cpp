#include "NarisSaveSubsystem.h"
#include "NarisSaveGame.h"
#include "NarisPlayerCharacter.h"
#include "NarisVitalsComponent.h"
#include "NarisInventoryComponent.h"
#include "NarisGatherCraftComponent.h"
#include "NarisQuestSubsystem.h"
#include "NarisWorldStateSubsystem.h"
#include "NarisChapterSubsystem.h"
#include "NarisEnemyCharacter.h"
#include "NarisPickupActor.h"
#include "Kismet/GameplayStatics.h"

bool UNarisSaveSubsystem::SavePlayer(ANarisPlayerCharacter* P,const FString& Slot)
{
 if(!P) return false;
 UNarisSaveGame* S=Cast<UNarisSaveGame>(UGameplayStatics::CreateSaveGameObject(UNarisSaveGame::StaticClass()));
 if(!S) return false;
 S->BuildID=TEXT("NARIS-0.7");
 S->WorldPackageName=P->GetWorld()?P->GetWorld()->GetOutermost()->GetName():FString();
 S->PlayerTransform=P->GetActorTransform();
 S->Health=P->Vitals?P->Vitals->Health:100.f;
 S->Energy=P->Vitals?P->Vitals->Energy:100.f;
 if(P->Inventory) for(const FNarisItemStack& I:P->Inventory->Items) S->Inventory.Add(I.ItemID,I.Quantity);
 if(P->GatherCraft) S->DepletedResourceNodes=P->GatherCraft->DepletedNodeIDs;
 if(UGameInstance* G=P->GetGameInstance()){
  if(UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>()) S->QuestRuntime=Q->GetRuntimeStates();
  if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>()){
   S->WorldFlags=W->GetFlags();
   S->Reputation=W->GetReputationMap();
  }
  if(UNarisChapterSubsystem* C=G->GetSubsystem<UNarisChapterSubsystem>()){
   S->CurrentChapter=(uint8)C->GetCurrentChapter();
   for(ENarisChapter V:C->GetUnlockedSet())S->UnlockedChapters.Add((uint8)V);
   for(ENarisChapter V:C->GetCompletedSet())S->CompletedChapters.Add((uint8)V);
  }
 }
 const bool bOK=UGameplayStatics::SaveGameToSlot(S,Slot,0);
 UE_LOG(LogTemp,Display,TEXT("NARIS_SAVE %s Slot=%s"),bOK?TEXT("PASS"):TEXT("FAIL"),*Slot);
 return bOK;
}
bool UNarisSaveSubsystem::LoadPlayer(ANarisPlayerCharacter* P,const FString& Slot)
{
 if(!P||!UGameplayStatics::DoesSaveGameExist(Slot,0)) return false;
 UNarisSaveGame* S=Cast<UNarisSaveGame>(UGameplayStatics::LoadGameFromSlot(Slot,0)); if(!S) return false;
 if(S->SchemaVersion!=GetDefault<UNarisSaveGame>()->SchemaVersion || S->PlayerTransform.ContainsNaN() || !FMath::IsFinite(S->Health) || !FMath::IsFinite(S->Energy)){
  UE_LOG(LogTemp,Warning,TEXT("NARIS_LOAD REJECTED Slot=%s Schema=%d"),*Slot,S->SchemaVersion);return false;
 }
 P->SetActorTransform(S->PlayerTransform,false,nullptr,ETeleportType::TeleportPhysics);
 if(P->Vitals){P->Vitals->Health=FMath::Clamp(S->Health,0.f,P->Vitals->MaxHealth);P->Vitals->Energy=FMath::Clamp(S->Energy,0.f,P->Vitals->MaxEnergy);}
 if(P->Inventory){P->Inventory->Items.Reset();for(const auto& K:S->Inventory)P->Inventory->AddItem(K.Key,K.Value);}
 if(P->GatherCraft) P->GatherCraft->DepletedNodeIDs=S->DepletedResourceNodes;
 if(UGameInstance* G=P->GetGameInstance()){
  if(UNarisQuestSubsystem* Q=G->GetSubsystem<UNarisQuestSubsystem>()) Q->RestoreRuntimeStates(S->QuestRuntime);
  if(UNarisWorldStateSubsystem* W=G->GetSubsystem<UNarisWorldStateSubsystem>()) W->RestoreState(S->WorldFlags,S->Reputation);
  if(UNarisChapterSubsystem* C=G->GetSubsystem<UNarisChapterSubsystem>()) C->RestoreState((ENarisChapter)S->CurrentChapter,S->UnlockedChapters,S->CompletedChapters);
 }
 TArray<AActor*> PersistentActors;
 UGameplayStatics::GetAllActorsOfClass(P,ANarisEnemyCharacter::StaticClass(),PersistentActors);
 for(AActor* A:PersistentActors) if(ANarisEnemyCharacter* E=Cast<ANarisEnemyCharacter>(A)) E->ApplyPersistentState();
 PersistentActors.Reset();
 UGameplayStatics::GetAllActorsOfClass(P,ANarisPickupActor::StaticClass(),PersistentActors);
 for(AActor* A:PersistentActors) if(ANarisPickupActor* Pickup=Cast<ANarisPickupActor>(A)) Pickup->ApplyPersistentState();

 UE_LOG(LogTemp,Display,TEXT("NARIS_LOAD PASS Slot=%s Schema=%d PersistentActorsRefreshed=1"),*Slot,S->SchemaVersion);
 return true;
}
