#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisWorldStateSubsystem.generated.h"

UCLASS()
class NARISCORE_API UNarisWorldStateSubsystem : public UGameInstanceSubsystem
{
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) void SetFlag(FName Flag,bool bValue);
 UFUNCTION(BlueprintPure) bool GetFlag(FName Flag) const;
 UFUNCTION(BlueprintCallable) int32 AddFactionReputation(FName FactionID,int32 Delta);
 UFUNCTION(BlueprintPure) int32 GetFactionReputation(FName FactionID) const;
 const TMap<FName,bool>& GetFlags() const { return Flags; }
 const TMap<FName,int32>& GetReputationMap() const { return FactionReputation; }
 void RestoreState(const TMap<FName,bool>& InFlags,const TMap<FName,int32>& InReputation);
private:
 UPROPERTY() TMap<FName,bool> Flags;
 UPROPERTY() TMap<FName,int32> FactionReputation;
};