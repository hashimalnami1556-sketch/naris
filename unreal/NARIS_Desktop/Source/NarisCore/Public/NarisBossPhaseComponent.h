#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisBossPhaseComponent.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisPhaseChanged,int32,OldPhase,int32,NewPhase);
UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisBossPhaseComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UPROPERTY(BlueprintReadOnly, Category="NARIS|Boss") int32 CurrentPhase=1;
 UPROPERTY(BlueprintAssignable, Category="NARIS|Boss") FNarisPhaseChanged OnPhaseChanged;
 UFUNCTION(BlueprintCallable, Category="NARIS|Boss") bool RequestPhase(int32 NewPhase){ if(NewPhase<=CurrentPhase) return false; int32 Old=CurrentPhase; CurrentPhase=NewPhase; OnPhaseChanged.Broadcast(Old,CurrentPhase); return true; }
};
