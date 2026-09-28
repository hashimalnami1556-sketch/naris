#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisVitalsComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNarisVitalsChanged, float, Current, float, Max);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNarisDeathEvent);

UCLASS(ClassGroup=(NARIS), meta=(BlueprintSpawnableComponent))
class NARISCORE_API UNarisVitalsComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 UNarisVitalsComponent();
 virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Vitals") float MaxHealth=100.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Vitals") float MaxEnergy=100.f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="NARIS|Vitals") float EnergyRegenPerSecond=18.f;
 UPROPERTY(BlueprintReadOnly, Category="NARIS|Vitals") float Health=100.f;
 UPROPERTY(BlueprintReadOnly, Category="NARIS|Vitals") float Energy=100.f;
 UPROPERTY(BlueprintAssignable) FNarisVitalsChanged OnHealthChanged;
 UPROPERTY(BlueprintAssignable) FNarisVitalsChanged OnEnergyChanged;
 UPROPERTY(BlueprintAssignable) FNarisDeathEvent OnDeath;
 UFUNCTION(BlueprintCallable) float ApplyHealthDamage(float Amount);
 UFUNCTION(BlueprintCallable) float Heal(float Amount);
 UFUNCTION(BlueprintCallable) bool SpendEnergy(float Amount);
 UFUNCTION(BlueprintPure) bool IsAlive() const { return Health>0.f; }
};