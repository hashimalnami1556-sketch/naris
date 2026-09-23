#include "NarisGameUserSettings.h"

#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Engine/Engine.h"
#include "Rendering/RenderingCommon.h"

UNarisGameUserSettings::UNarisGameUserSettings(
    const FObjectInitializer& ObjectInitializer
)
    : Super(ObjectInitializer)
{
}

void UNarisGameUserSettings::SetToDefaults()
{
    Super::SetToDefaults();

    MasterVolume = 1.f;
    MusicVolume = 0.8f;
    SFXVolume = 1.f;
    VoiceVolume = 1.f;

    bSubtitlesEnabled = true;
    SubtitleScale = 1.f;
    bReduceCameraShake = false;
    CameraShakeIntensity = 1.f;
    bHighContrastInteractions = false;
    ColorVisionMode = ENarisColorVisionMode::Normal;
    ColorVisionSeverity = 0.f;
    bCorrectColorVisionDeficiency = true;

    SetVSyncEnabled(true);
    SetFrameRateLimit(120.f);
    SetOverallScalabilityLevel(3);
}

void UNarisGameUserSettings::ValidateSettings()
{
    Super::ValidateSettings();

    MasterVolume = FMath::Clamp(MasterVolume, 0.f, 1.f);
    MusicVolume = FMath::Clamp(MusicVolume, 0.f, 1.f);
    SFXVolume = FMath::Clamp(SFXVolume, 0.f, 1.f);
    VoiceVolume = FMath::Clamp(VoiceVolume, 0.f, 1.f);

    SubtitleScale = FMath::Clamp(SubtitleScale, 0.75f, 2.f);
    CameraShakeIntensity = FMath::Clamp(CameraShakeIntensity, 0.f, 1.5f);
    ColorVisionSeverity = FMath::Clamp(ColorVisionSeverity, 0.f, 1.f);
}

void UNarisGameUserSettings::ApplyNonResolutionSettings()
{
    Super::ApplyNonResolutionSettings();
    ValidateSettings();

    EColorVisionDeficiency Deficiency = EColorVisionDeficiency::NormalVision;

    switch (ColorVisionMode)
    {
        case ENarisColorVisionMode::Deuteranopia:
            Deficiency = EColorVisionDeficiency::Deuteranope;
            break;
        case ENarisColorVisionMode::Protanopia:
            Deficiency = EColorVisionDeficiency::Protanope;
            break;
        case ENarisColorVisionMode::Tritanopia:
            Deficiency = EColorVisionDeficiency::Tritanope;
            break;
        case ENarisColorVisionMode::Normal:
        default:
            break;
    }

    UWidgetBlueprintLibrary::SetColorVisionDeficiencyType(
        Deficiency,
        ColorVisionSeverity,
        bCorrectColorVisionDeficiency,
        false
    );
}

UNarisGameUserSettings* UNarisGameUserSettings::GetNarisGameUserSettings()
{
    if (!GEngine)
    {
        return nullptr;
    }

    return Cast<UNarisGameUserSettings>(GEngine->GetGameUserSettings());
}

void UNarisGameUserSettings::ApplyAndSave(
    bool bCheckForCommandLineOverrides
)
{
    ValidateSettings();
    ApplySettings(bCheckForCommandLineOverrides);
}

void UNarisGameUserSettings::SetQualityPreset(int32 QualityLevel)
{
    SetOverallScalabilityLevel(FMath::Clamp(QualityLevel, 0, 4));
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetMasterVolume(float Value)
{
    MasterVolume = FMath::Clamp(Value, 0.f, 1.f);
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetMusicVolume(float Value)
{
    MusicVolume = FMath::Clamp(Value, 0.f, 1.f);
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetSFXVolume(float Value)
{
    SFXVolume = FMath::Clamp(Value, 0.f, 1.f);
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetVoiceVolume(float Value)
{
    VoiceVolume = FMath::Clamp(Value, 0.f, 1.f);
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetSubtitlesEnabled(bool bEnabled)
{
    bSubtitlesEnabled = bEnabled;
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetReduceCameraShake(bool bEnabled)
{
    bReduceCameraShake = bEnabled;
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetHighContrastInteractions(bool bEnabled)
{
    bHighContrastInteractions = bEnabled;
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetCameraShakeIntensity(float Value)
{
    CameraShakeIntensity = FMath::Clamp(Value, 0.f, 1.5f);
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetSubtitleScale(float Value)
{
    SubtitleScale = FMath::Clamp(Value, 0.75f, 2.f);
    RequestUIUpdate();
}

void UNarisGameUserSettings::SetColorVisionMode(
    ENarisColorVisionMode Mode,
    float Severity,
    bool bCorrectDeficiency
)
{
    ColorVisionMode = Mode;
    ColorVisionSeverity = FMath::Clamp(Severity, 0.f, 1.f);
    bCorrectColorVisionDeficiency = bCorrectDeficiency;
    RequestUIUpdate();
}

float UNarisGameUserSettings::GetPresentationSFXScale() const
{
    return FMath::Clamp(MasterVolume * SFXVolume, 0.f, 1.f);
}

float UNarisGameUserSettings::GetPresentationMusicScale() const
{
    return FMath::Clamp(MasterVolume * MusicVolume, 0.f, 1.f);
}

float UNarisGameUserSettings::GetPresentationVoiceScale() const
{
    return FMath::Clamp(MasterVolume * VoiceVolume, 0.f, 1.f);
}

float UNarisGameUserSettings::GetEffectiveCameraShakeScale() const
{
    const float AuthoredScale = FMath::Clamp(CameraShakeIntensity, 0.f, 1.5f);
    return bReduceCameraShake
        ? FMath::Min(AuthoredScale, 0.35f)
        : AuthoredScale;
}
