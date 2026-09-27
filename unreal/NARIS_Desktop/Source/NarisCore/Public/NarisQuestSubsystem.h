#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisNarrativeTypes.h"
#include "NarisQuestSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisQuestStateChanged,FName,QuestID,bool,bCompleted);

UCLASS()
class NARISCORE_API UNarisQuestSubsystem : public UGameInstanceSubsystem
{
 GENERATED_BODY()
public:
 UPROPERTY(BlueprintAssignable) FNarisQuestStateChanged OnQuestStateChanged;
 UFUNCTION(BlueprintCallable) bool StartQuest(FName QuestID);
 UFUNCTION(BlueprintCallable) void PublishNarrativeEvent(const FNarisNarrativeEvent& Event);
 UFUNCTION(BlueprintPure) bool IsQuestCompleted(FName QuestID) const;
 UFUNCTION(BlueprintPure) bool IsQuestActive(FName QuestID) const;
 UFUNCTION(BlueprintPure) int32 GetObjectiveProgress(FName QuestID,FName TargetID,ENarisNarrativeEventType Type) const;
 const TMap<FName,FNarisQuestRuntimeState>& GetRuntimeStates() const { return Runtime; }
 void RestoreRuntimeStates(const TMap<FName,FNarisQuestRuntimeState>& InStates);
private:
 UPROPERTY() TMap<FName,FNarisQuestRuntimeState> Runtime;
 void EvaluateQuest(FNarisQuestRuntimeState& State);
};