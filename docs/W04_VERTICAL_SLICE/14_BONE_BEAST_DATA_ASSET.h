#pragma once

// NARIS W04 scaffold contract for a Primary Data Asset.

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "BoneBeastDataAsset.generated.h"

USTRUCT(BlueprintType)
struct FNarisBossAttackDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName AttackId;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float Damage = 0.0f; // TUNE

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float TelegraphDuration = 0.0f; // TUNE

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float RecoveryDuration = 0.0f; // TUNE

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName AnimationMontageId;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName ImpactEvent;
};

USTRUCT(BlueprintType)
struct FNarisBossPhaseDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName PhaseId;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float HealthThreshold = 0.0f; // TUNE

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TArray<FNarisBossAttackDefinition> Attacks;
};

UCLASS(BlueprintType)
class NARIS_API UBoneBeastDataAsset : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    FName BossId = TEXT("BoneBeast");

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Boss")
    TArray<FNarisBossPhaseDefinition> Phases;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Quest")
    FName QuestCompletionId;
};
