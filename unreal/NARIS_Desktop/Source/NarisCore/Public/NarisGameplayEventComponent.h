#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisCombatTypes.h"
#include "NarisGameplayEventComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FNarisGameplayEventSignature, ENarisGameplayEventType, Type, FName, EventID, FName, ContextID);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisGameplayEventComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UPROPERTY(BlueprintAssignable, Category="NARIS|Events") FNarisGameplayEventSignature OnGameplayEvent;
 UFUNCTION(BlueprintCallable, Category="NARIS|Events") void Emit(ENarisGameplayEventType Type, FName EventID, FName ContextID) { OnGameplayEvent.Broadcast(Type, EventID, ContextID); }
};
