#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BoneBeastCombatComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisCombatEvent, FName, EventName);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UBoneBeastCombatComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void StartAttack(FName AttackId);

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void ResolveImpact(float Damage);

    UFUNCTION(BlueprintCallable, Category="NARIS|Combat")
    void TriggerStagger();

    UPROPERTY(BlueprintAssignable, Category="NARIS|Combat")
    FNarisCombatEvent OnCombatEvent;
};
