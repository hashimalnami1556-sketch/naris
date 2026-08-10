#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BoneBeastPhaseComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisBossPhaseEvent, FName, PhaseId);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARIS_API UBoneBeastPhaseComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UBoneBeastPhaseComponent();

    UFUNCTION(BlueprintCallable)
    void EvaluateHealth(float CurrentHealth, float MaxHealth);

    UPROPERTY(BlueprintAssignable)
    FNarisBossPhaseEvent OnPhaseTransition;

private:
    int32 LastPhaseIndex = 0;
};
