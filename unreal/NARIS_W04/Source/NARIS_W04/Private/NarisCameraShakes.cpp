#include "NarisCameraShakes.h"

#include "Shakes/PerlinNoiseCameraShakePattern.h"

UNarisCameraShakeBase::UNarisCameraShakeBase(
    const FObjectInitializer& ObjectInitializer
)
    : Super(ObjectInitializer)
{
    bSingleInstance = false;
}

void UNarisCameraShakeBase::ConfigurePerlin(
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
)
{
    UPerlinNoiseCameraShakePattern* Pattern =
        Cast<UPerlinNoiseCameraShakePattern>(GetRootShakePattern());

    if (!Pattern)
    {
        Pattern = ChangeRootShakePattern<UPerlinNoiseCameraShakePattern>();
    }

    if (!Pattern)
    {
        return;
    }

    Pattern->Duration = FMath::Max(Duration, 0.01f);
    Pattern->BlendInTime = FMath::Clamp(BlendIn, 0.f, Pattern->Duration);
    Pattern->BlendOutTime = FMath::Clamp(BlendOut, 0.f, Pattern->Duration);

    Pattern->LocationAmplitudeMultiplier = FMath::Max(LocationAmplitude, 0.f);
    Pattern->LocationFrequencyMultiplier = FMath::Max(LocationFrequency, 0.f);
    Pattern->RotationAmplitudeMultiplier = FMath::Max(RotationAmplitude, 0.f);
    Pattern->RotationFrequencyMultiplier = FMath::Max(RotationFrequency, 0.f);

    Pattern->X.Amplitude = 0.35f;
    Pattern->X.Frequency = 11.f;
    Pattern->Y.Amplitude = 0.45f;
    Pattern->Y.Frequency = 12.f;
    Pattern->Z.Amplitude = 0.55f;
    Pattern->Z.Frequency = 13.f;

    Pattern->Pitch.Amplitude = PitchAmplitude;
    Pattern->Pitch.Frequency = 14.f;
    Pattern->Yaw.Amplitude = YawAmplitude;
    Pattern->Yaw.Frequency = 13.f;
    Pattern->Roll.Amplitude = RollAmplitude;
    Pattern->Roll.Frequency = 12.f;

    Pattern->FOV.Amplitude = FOVAmplitude;
    Pattern->FOV.Frequency = 10.f;
}

UNarisHitCameraShake::UNarisHitCameraShake(
    const FObjectInitializer& ObjectInitializer
)
    : Super(ObjectInitializer)
{
    ConfigurePerlin(
        0.12f,
        0.015f,
        0.06f,
        0.7f,
        1.0f,
        0.85f,
        1.0f,
        0.45f,
        0.35f,
        0.15f,
        0.15f
    );
}

UNarisHeavyCameraShake::UNarisHeavyCameraShake(
    const FObjectInitializer& ObjectInitializer
)
    : Super(ObjectInitializer)
{
    ConfigurePerlin(
        0.20f,
        0.02f,
        0.10f,
        1.4f,
        0.9f,
        1.65f,
        0.85f,
        1.0f,
        0.75f,
        0.45f,
        0.35f
    );
}

UNarisParryCameraShake::UNarisParryCameraShake(
    const FObjectInitializer& ObjectInitializer
)
    : Super(ObjectInitializer)
{
    ConfigurePerlin(
        0.15f,
        0.01f,
        0.08f,
        0.55f,
        1.25f,
        1.35f,
        1.2f,
        0.75f,
        0.55f,
        0.20f,
        0.18f
    );
}

UNarisPhaseCameraShake::UNarisPhaseCameraShake(
    const FObjectInitializer& ObjectInitializer
)
    : Super(ObjectInitializer)
{
    ConfigurePerlin(
        0.42f,
        0.05f,
        0.20f,
        1.8f,
        0.65f,
        2.1f,
        0.65f,
        1.2f,
        0.95f,
        0.55f,
        0.40f
    );
}

UNarisDeathCameraShake::UNarisDeathCameraShake(
    const FObjectInitializer& ObjectInitializer
)
    : Super(ObjectInitializer)
{
    ConfigurePerlin(
        0.65f,
        0.05f,
        0.30f,
        2.4f,
        0.55f,
        2.8f,
        0.55f,
        1.55f,
        1.2f,
        0.75f,
        0.55f
    );
}
