#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisGameplayTypes.h"
#include "NarisCombatComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisCombatEvent, FNarisCombatResult, Result);

UCLASS(ClassGroup=(NARIS), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisCombatComponent : public UActorComponent {
    GENERATED_BODY()
public:
    UNarisCombatComponent();
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat") float MaxHealth=100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat") float Health=100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat") float MaxPoise=100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat") float Poise=100.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resonance") float Resonance=0.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Resonance") float MaxResonance=100.f;
    UPROPERTY(BlueprintAssignable) FNarisCombatEvent OnCombatResolved;
    UFUNCTION(BlueprintCallable, Category="NARIS|Combat") FNarisCombatResult ResolveHit(float BaseDamage,float PoiseDamage,bool bParried,bool bCritical);
    UFUNCTION(BlueprintCallable, Category="NARIS|Combat") void AddResonance(float Amount);
    UFUNCTION(BlueprintCallable, Category="NARIS|Combat") void ResetPoise();
};