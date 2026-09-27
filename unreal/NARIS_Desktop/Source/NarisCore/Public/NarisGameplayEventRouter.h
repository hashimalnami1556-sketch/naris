#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameplayTagContainer.h"
#include "NarisGameplayEventRouter.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisGameplayEvent,FGameplayTag,EventTag,FName,PayloadID);
UCLASS(ClassGroup=(NARIS),meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisGameplayEventRouter: public UActorComponent { GENERATED_BODY() public: UPROPERTY(BlueprintAssignable) FNarisGameplayEvent OnGameplayEvent; UFUNCTION(BlueprintCallable) void EmitEvent(FGameplayTag EventTag,FName PayloadID){OnGameplayEvent.Broadcast(EventTag,PayloadID);} };
