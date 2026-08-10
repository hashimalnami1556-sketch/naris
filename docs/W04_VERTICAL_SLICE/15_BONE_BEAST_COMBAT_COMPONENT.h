#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BoneBeastCombatComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisBossCombatEvent, FName, EventName);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARIS_API UBoneBeastCombatComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UBoneBeastCombatComponent();

    UFUNCTION(BlueprintCallable)
    void StartAttack(FName AttackId);

    UFUNCTION(BlueprintCallable)
    void ResolveImpact(float Damage);

    UFUNCTION(BlueprintCallable)
    void TriggerStagger();

    UPROPERTY(BlueprintAssignable)
    FNarisBossCombatEvent OnCombatEvent;
};
