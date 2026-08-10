#pragma once

#include "CoreMinimal.h"
#include "NarisW04Types.generated.h"

UENUM(BlueprintType)
enum class ENarisBossPhase : uint8
{
    Phase1 UMETA(DisplayName="Phase 1"),
    Phase2 UMETA(DisplayName="Phase 2"),
    Phase3 UMETA(DisplayName="Phase 3"),
    Dead   UMETA(DisplayName="Dead")
};

USTRUCT(BlueprintType)
struct FNarisBossAttackDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName AttackId;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float Damage = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float TelegraphDuration = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float RecoveryDuration = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName AnimationMontageId;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName ImpactEvent;
};
