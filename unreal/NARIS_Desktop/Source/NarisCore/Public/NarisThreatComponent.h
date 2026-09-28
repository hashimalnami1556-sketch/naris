#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisThreatComponent.generated.h"
USTRUCT(BlueprintType) struct FNarisThreatEntry { GENERATED_BODY() UPROPERTY(BlueprintReadOnly) TObjectPtr<AActor> Actor=nullptr; UPROPERTY(BlueprintReadOnly) float Threat=0.f; };
UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisThreatComponent : public UActorComponent {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) void AddThreat(AActor* Source, float Amount);
 UFUNCTION(BlueprintCallable) void RemoveThreat(AActor* Source);
 UFUNCTION(BlueprintPure) AActor* GetHighestThreatTarget() const;
 UFUNCTION(BlueprintCallable) void DecayThreat(float DeltaSeconds, float RatePerSecond=2.f);
private: UPROPERTY() TArray<FNarisThreatEntry> Entries;
};
