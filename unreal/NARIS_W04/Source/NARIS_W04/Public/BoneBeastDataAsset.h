#pragma once

#include "CoreMinimal.h"
#include "Engine/PrimaryDataAsset.h"
#include "NarisW04Types.h"
#include "BoneBeastDataAsset.generated.h"

USTRUCT(BlueprintType)
struct FNarisBossPhaseDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName PhaseId;

    // Deliberately tune in editor/playtest; no source-defined numeric value is assumed here.
    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float HealthThreshold = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TArray<FNarisBossAttackDefinition> Attacks;
};

UCLASS(BlueprintType)
class NARIS_W04_API UBoneBeastDataAsset : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    FName BossId = TEXT("BoneBeast");

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    float MaxHealth = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    TArray<FNarisBossPhaseDefinition> Phases;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Quest")
    FName QuestCompletionId;
};
