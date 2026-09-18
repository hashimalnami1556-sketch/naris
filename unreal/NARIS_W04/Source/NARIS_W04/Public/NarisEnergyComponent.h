#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisGameplayTypes.h"
#include "NarisEnergyComponent.generated.h"

UCLASS(ClassGroup=(NARIS), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisEnergyComponent : public UActorComponent {
    GENERATED_BODY()
public:
    UNarisEnergyComponent();
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Energy") float MaxEnergy=100.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Energy") float Energy=100.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Energy") ENarisEssence ActiveEssence=ENarisEssence::NarisFlame;
    UFUNCTION(BlueprintCallable,Category="NARIS|Energy") bool Spend(float Amount);
    UFUNCTION(BlueprintCallable,Category="NARIS|Energy") void Restore(float Amount);
    UFUNCTION(BlueprintCallable,Category="NARIS|Energy") void SetEssence(ENarisEssence NewEssence);
};