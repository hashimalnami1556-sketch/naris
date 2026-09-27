#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisDynamicEventComponent.generated.h"

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisDynamicEventComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) bool CanTriggerEvent(FName EventID, float CooldownSeconds) const;
 UFUNCTION(BlueprintCallable) void MarkTriggered(FName EventID);
private:
 UPROPERTY() TMap<FName,double> LastTriggered;
};
