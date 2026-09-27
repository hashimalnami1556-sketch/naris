#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "NarisWorldSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisZoneChanged, FName, PreviousZone, FName, NewZone);

UCLASS()
class NARISCORE_API UNarisWorldSubsystem : public UWorldSubsystem {
 GENERATED_BODY()
public:
 UPROPERTY(BlueprintAssignable) FNarisZoneChanged OnZoneChanged;
 UFUNCTION(BlueprintCallable) void SetActiveZone(FName ZoneID);
 UFUNCTION(BlueprintPure) FName GetActiveZone() const { return ActiveZone; }
 UFUNCTION(BlueprintPure) int32 MakeDeterministicSeed(FName ZoneID, int32 LayerSeed) const;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 WorldSeed = 731947;
private:
 UPROPERTY() FName ActiveZone;
};
