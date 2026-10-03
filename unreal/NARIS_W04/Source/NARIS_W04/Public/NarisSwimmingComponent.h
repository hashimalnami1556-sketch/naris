#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NarisSwimmingComponent.generated.h"

class ANarisWaterVolume;
class ACharacter;
class UNarisCombatComponent;

UCLASS(ClassGroup=(NARIS), Blueprintable, meta=(BlueprintSpawnableComponent))
class NARIS_W04_API UNarisSwimmingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UNarisSwimmingComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(
        float DeltaTime,
        ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction
    ) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float MaxBreath = 30.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float BreathRecoveryPerSecond = 8.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float DrowningDamagePerSecond = 10.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float SwimSpeed = 420.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float VerticalSwimSpeed = 220.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Water")
    float HeadHeightOffset = 70.f;

    UFUNCTION(BlueprintCallable, Category="NARIS|Water")
    void EnterWater(ANarisWaterVolume* WaterVolume);

    UFUNCTION(BlueprintCallable, Category="NARIS|Water")
    void ExitWater(ANarisWaterVolume* WaterVolume);

    UFUNCTION(BlueprintCallable, Category="NARIS|Water")
    void SetVerticalSwimInput(float Value);

    UFUNCTION(BlueprintPure, Category="NARIS|Water")
    bool IsSwimming() const { return bSwimming; }

    UFUNCTION(BlueprintPure, Category="NARIS|Water")
    bool IsUnderwater() const { return bUnderwater; }

    UFUNCTION(BlueprintPure, Category="NARIS|Water")
    float GetBreathPercent() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Water")
    float GetBreathRemaining() const { return BreathRemaining; }

private:
    void UpdateWaterState(float DeltaTime);
    void ApplyCurrent(float DeltaTime);
    void ApplyDrowning(float DeltaTime);

    TWeakObjectPtr<ANarisWaterVolume> ActiveWaterVolume;
    TWeakObjectPtr<ACharacter> CharacterOwner;
    TWeakObjectPtr<UNarisCombatComponent> Combat;

    float BreathRemaining = 30.f;
    float VerticalInput = 0.f;
    bool bSwimming = false;
    bool bUnderwater = false;
};
