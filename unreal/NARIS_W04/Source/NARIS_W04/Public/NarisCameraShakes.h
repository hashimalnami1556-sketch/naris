#pragma once

#include "CoreMinimal.h"
#include "Shakes/DefaultCameraShakeBase.h"
#include "NarisCameraShakes.generated.h"

UCLASS(Abstract)
class NARIS_W04_API UNarisCameraShakeBase : public UDefaultCameraShakeBase
{
    GENERATED_BODY()

public:
    UNarisCameraShakeBase(const FObjectInitializer& ObjectInitializer);

protected:
    void ConfigurePerlin(
        float Duration,
        float BlendIn,
        float BlendOut,
        float LocationAmplitude,
        float LocationFrequency,
        float RotationAmplitude,
        float RotationFrequency,
        float PitchAmplitude,
        float YawAmplitude,
        float RollAmplitude,
        float FOVAmplitude
    );
};

UCLASS()
class NARIS_W04_API UNarisHitCameraShake : public UNarisCameraShakeBase
{
    GENERATED_BODY()

public:
    UNarisHitCameraShake(const FObjectInitializer& ObjectInitializer);
};

UCLASS()
class NARIS_W04_API UNarisHeavyCameraShake : public UNarisCameraShakeBase
{
    GENERATED_BODY()

public:
    UNarisHeavyCameraShake(const FObjectInitializer& ObjectInitializer);
};

UCLASS()
class NARIS_W04_API UNarisParryCameraShake : public UNarisCameraShakeBase
{
    GENERATED_BODY()

public:
    UNarisParryCameraShake(const FObjectInitializer& ObjectInitializer);
};

UCLASS()
class NARIS_W04_API UNarisPhaseCameraShake : public UNarisCameraShakeBase
{
    GENERATED_BODY()

public:
    UNarisPhaseCameraShake(const FObjectInitializer& ObjectInitializer);
};

UCLASS()
class NARIS_W04_API UNarisDeathCameraShake : public UNarisCameraShakeBase
{
    GENERATED_BODY()

public:
    UNarisDeathCameraShake(const FObjectInitializer& ObjectInitializer);
};
