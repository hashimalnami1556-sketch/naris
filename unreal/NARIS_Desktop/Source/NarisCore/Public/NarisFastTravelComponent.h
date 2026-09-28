#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisFastTravelComponent.generated.h"
UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisFastTravelComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) void UnlockNode(FName NodeID);
 UFUNCTION(BlueprintPure) bool IsNodeUnlocked(FName NodeID) const;
private:
 UPROPERTY(SaveGame) TSet<FName> UnlockedNodes;
};
