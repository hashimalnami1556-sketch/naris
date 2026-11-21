#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "NarisWolfAnimInstance.generated.h"

// Parent class referenced by existing ABP_CelestialWolf V9.
// Exposes the real native input required by the existing BS_Wolf_Locomotion graph.
UCLASS(Blueprintable, BlueprintType)
class NARIS_W04_API UNarisWolfAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NARIS|Wolf|Locomotion")
    float SmoothedSpeed = 0.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="NARIS|Wolf|Locomotion", meta=(ClampMin="0.0"))
    float SpeedInterpolationRate = 8.f;

    virtual void NativeInitializeAnimation() override;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;
};
