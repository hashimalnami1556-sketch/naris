#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "NarisGameUserSettings.generated.h"

UENUM(BlueprintType)
enum class ENarisColorVisionMode : uint8
{
    Normal,
    Deuteranopia,
    Protanopia,
    Tritanopia
};

UCLASS(Config=GameUserSettings, ConfigDoNotCheckDefaults, BlueprintType)
class NARIS_W04_API UNarisGameUserSettings : public UGameUserSettings
{
    GENERATED_BODY()

public:
    UNarisGameUserSettings(const FObjectInitializer& ObjectInitializer);

    virtual void SetToDefaults() override;
    virtual void ValidateSettings() override;
    virtual void ApplyNonResolutionSettings() override;

    UFUNCTION(BlueprintPure, Category="NARIS|Settings")
    static UNarisGameUserSettings* GetNarisGameUserSettings();

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings")
    void ApplyAndSave(bool bCheckForCommandLineOverrides = true);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Graphics")
    void SetQualityPreset(int32 QualityLevel);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Audio")
    void SetMasterVolume(float Value);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Audio")
    void SetMusicVolume(float Value);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Audio")
    void SetSFXVolume(float Value);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Audio")
    void SetVoiceVolume(float Value);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Accessibility")
    void SetCameraShakeIntensity(float Value);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Accessibility")
    void SetSubtitleScale(float Value);

    UFUNCTION(BlueprintCallable, Category="NARIS|Settings|Accessibility")
    void SetColorVisionMode(
        ENarisColorVisionMode Mode,
        float Severity,
        bool bCorrectDeficiency
    );

    UFUNCTION(BlueprintPure, Category="NARIS|Settings|Audio")
    float GetPresentationSFXScale() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Settings|Accessibility")
    float GetEffectiveCameraShakeScale() const;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Audio")
    float MasterVolume = 1.f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Audio")
    float MusicVolume = 0.8f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Audio")
    float SFXVolume = 1.f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Audio")
    float VoiceVolume = 1.f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    bool bSubtitlesEnabled = true;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    float SubtitleScale = 1.f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    bool bReduceCameraShake = false;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    float CameraShakeIntensity = 1.f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    bool bHighContrastInteractions = false;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    ENarisColorVisionMode ColorVisionMode = ENarisColorVisionMode::Normal;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    float ColorVisionSeverity = 0.f;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Accessibility")
    bool bCorrectColorVisionDeficiency = true;
};
