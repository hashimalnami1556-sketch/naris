#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisEncounterDirectorComponent.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisIntensityChanged,float,OldIntensity,float,NewIntensity);
UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisEncounterDirectorComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Intensity=0.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float TargetIntensity=.35f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 ActiveEnemyBudget=8;
 UPROPERTY(BlueprintAssignable) FNarisIntensityChanged OnIntensityChanged;
 UFUNCTION(BlueprintCallable) void ReportPlayerPressure(float HealthPct,float RecentDamage,float NearbyEnemies);
 UFUNCTION(BlueprintCallable) bool CanSpawnCost(int32 Cost) const { return Cost<=ActiveEnemyBudget; }
 UFUNCTION(BlueprintCallable) void ConsumeBudget(int32 Cost){ActiveEnemyBudget=FMath::Max(0,ActiveEnemyBudget-Cost);}
 UFUNCTION(BlueprintCallable) void RefundBudget(int32 Cost){ActiveEnemyBudget+=FMath::Max(0,Cost);}
};
