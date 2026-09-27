#pragma once
#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "NarisNarrativeTypes.generated.h"

UENUM(BlueprintType)
enum class ENarisNarrativeEventType : uint8 { Interact, EnemyDefeated, BossDefeated, ZoneDiscovered, EncounterCompleted, ItemAcquired, DialogueChoice };

USTRUCT(BlueprintType)
struct FNarisNarrativeEvent {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadWrite) ENarisNarrativeEventType Type = ENarisNarrativeEventType::Interact;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) FName TargetID = NAME_None;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) FName InstigatorID = NAME_None;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Amount = 1;
};

USTRUCT(BlueprintType)
struct FNarisQuestRuntimeState {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadWrite) FName QuestID = NAME_None;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bActive = false;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bCompleted = false;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) TMap<FName,int32> ObjectiveProgress;
};
