#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BoneBeastPhaseComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisPhaseEvent, FName, PhaseId);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UBoneBeastPhaseComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="NARIS|Boss")
    void EvaluateHealth(float CurrentHealth, float MaxHealth);

    UPROPERTY(BlueprintAssignable, Category="NARIS|Boss")
    FNarisPhaseEvent OnPhaseTransition;

private:
    int32 LastPhaseIndex = 0;
};
