#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisCodexSubsystem.generated.h"
UCLASS()
class NARISCORE_API UNarisCodexSubsystem : public UGameInstanceSubsystem {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) bool UnlockEntry(FName CodexID);
 UFUNCTION(BlueprintPure) bool IsUnlocked(FName CodexID) const;
private: UPROPERTY() TSet<FName> Unlocked;
};
