#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisVFXDirectorComponent.generated.h"
class UNiagaraSystem;

UCLASS(ClassGroup=(NARIS),meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisVFXDirectorComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UNarisVFXDirectorComponent();
 UFUNCTION(BlueprintCallable) void SpawnVFX(FName EventID,FVector Location,FRotator Rotation=FRotator::ZeroRotator,float Scale=1.f);
 UFUNCTION(BlueprintPure) bool IsCombatVFXReady() const;
private:
 UPROPERTY() TObjectPtr<UNiagaraSystem> RadialBurst;
 UPROPERTY() TObjectPtr<UNiagaraSystem> DirectionalBurst;
 UPROPERTY() TObjectPtr<UNiagaraSystem> SimpleExplosion;
 UNiagaraSystem* Resolve(FName EventID) const;
};