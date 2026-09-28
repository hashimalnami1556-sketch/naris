#include "NarisQuestSubsystem.h"
#include "NarisGameModeBase.h"
#include "NarisAudioDirectorComponent.h"
#include "NarisVFXDirectorComponent.h"
#include "NarisChapterSubsystem.h"
#include "Kismet/GameplayStatics.h"

static FName NarisObjectiveKey(FName Target,ENarisNarrativeEventType Type)
{
 return FName(*FString::Printf(TEXT("%s:%d"),*Target.ToString(),(int32)Type));
}
bool UNarisQuestSubsystem::StartQuest(FName ID)
{
 if(ID.IsNone()) return false;
 auto& S=Runtime.FindOrAdd(ID); if(S.bCompleted) return false;
 S.QuestID=ID; S.bActive=true; OnQuestStateChanged.Broadcast(ID,false); return true;
}
void UNarisQuestSubsystem::PublishNarrativeEvent(const FNarisNarrativeEvent& Event)
{
 for(auto& Pair:Runtime){
  auto& S=Pair.Value; if(!S.bActive||S.bCompleted) continue;
  S.ObjectiveProgress.FindOrAdd(NarisObjectiveKey(Event.TargetID,Event.Type))+=FMath::Max(1,Event.Amount);
  EvaluateQuest(S);
 }
}
void UNarisQuestSubsystem::EvaluateQuest(FNarisQuestRuntimeState& S)
{
 if(S.QuestID!=FName("Q_AshenGate")||S.bCompleted) return;
 const int32 Shards=S.ObjectiveProgress.FindRef(NarisObjectiveKey(FName("AshShard"),ENarisNarrativeEventType::ItemAcquired));
 const int32 Beasts=S.ObjectiveProgress.FindRef(NarisObjectiveKey(FName("BoneBeast"),ENarisNarrativeEventType::EnemyDefeated));
 const int32 Boss=S.ObjectiveProgress.FindRef(NarisObjectiveKey(FName("GateWarden"),ENarisNarrativeEventType::BossDefeated));
 if(Shards>=3&&Beasts>=3&&Boss>=1){
  S.bCompleted=true; S.bActive=false; OnQuestStateChanged.Broadcast(S.QuestID,true);
  if(UWorld* W=GetWorld()) if(ANarisGameModeBase* GM=Cast<ANarisGameModeBase>(UGameplayStatics::GetGameMode(W))){
   if(GM->AudioDirector) GM->AudioDirector->PlaySFX(FName("QuestComplete"),FVector::ZeroVector,1.f);
   if(GM->VFXDirector){
    const FVector L=UGameplayStatics::GetPlayerPawn(W,0)?UGameplayStatics::GetPlayerPawn(W,0)->GetActorLocation():FVector::ZeroVector;
    GM->VFXDirector->SpawnVFX(FName("QuestComplete"),L+FVector(0,0,100.f),FRotator::ZeroRotator,1.25f);
   }
  }
  if(UGameInstance* G=GetGameInstance()) if(UNarisChapterSubsystem* C=G->GetSubsystem<UNarisChapterSubsystem>()){C->CompleteChapter(ENarisChapter::AshenGate);C->UnlockChapter(ENarisChapter::BellMarsh);}
  UE_LOG(LogTemp,Display,TEXT("NARIS_QUEST_COMPLETE Q_AshenGate Chapter1=Complete Chapter2=Unlocked"));
 }
}
bool UNarisQuestSubsystem::IsQuestCompleted(FName ID) const {if(const auto* S=Runtime.Find(ID))return S->bCompleted;return false;}
bool UNarisQuestSubsystem::IsQuestActive(FName ID) const {if(const auto* S=Runtime.Find(ID))return S->bActive&&!S->bCompleted;return false;}
int32 UNarisQuestSubsystem::GetObjectiveProgress(FName ID,FName Target,ENarisNarrativeEventType Type) const
{
 if(const auto* S=Runtime.Find(ID)) return S->ObjectiveProgress.FindRef(NarisObjectiveKey(Target,Type));
 return 0;
}
void UNarisQuestSubsystem::RestoreRuntimeStates(const TMap<FName,FNarisQuestRuntimeState>& InStates){Runtime=InStates;}
