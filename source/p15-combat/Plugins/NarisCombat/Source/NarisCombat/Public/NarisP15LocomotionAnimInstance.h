#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "NarisControlMotion.h"
#include "NarisP15CombatComponent.h"
#include "NarisP15LocomotionAnimInstance.generated.h"

// A data source for an authored Animation Blueprint, not an Animation Blueprint asset.
UCLASS(Transient, Blueprintable)
class NARISCOMBAT_API UNarisP15LocomotionAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") float Speed = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") float DirectionDegrees = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") float LeanDegrees = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") bool bStarting = false;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") bool bStopping = false;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") bool bPivoting = false;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") bool bFalling = false;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") bool bInCombat = false;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") bool bShouldTurnInPlace = false;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Locomotion") float FacingYawDelta = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Naris|Control") ENarisP15ControlPhase ControlPhase = ENarisP15ControlPhase::Unavailable;
    virtual void NativeInitializeAnimation() override;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
private:
    NarisP15::LocomotionSignals Signals;
};
