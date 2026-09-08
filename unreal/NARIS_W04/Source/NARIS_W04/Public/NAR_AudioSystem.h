// NAR_AudioSystem.h — نظام الصوت الكامل
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_AudioSystem.generated.h"

// ============================================
// أنواع الصوت
// ============================================
UENUM(BlueprintType)
enum class EAudioType : uint8
{
    Music       UMETA(DisplayName = "موسيقى"),
    SFX         UMETA(DisplayName = "مؤثر صوتي"),
    Ambient     UMETA(DisplayName = "صوت محيطي"),
    UI          UMETA(DisplayName = "واجهة المستخدم"),
    Dialogue    UMETA(DisplayName = "حوار")
};

// ============================================
// إعدادات الصوت
// ============================================
USTRUCT(BlueprintType)
struct FAudioSettings
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    float MasterVolume = 1.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    float MusicVolume = 0.7f;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    float SFXVolume = 1.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    float AmbientVolume = 0.8f;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    float UIVolume = 1.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    float DialogueVolume = 1.0f;

    UPROPERTY(BlueprintReadWrite, Category = "Audio")
    bool bMuted = false;
};

/**
 * UNAR_AudioSystem — نظام الصوت
 * يدير: الموسيقى + المؤثرات الصوتية + الأصوات المحيطية + الحوارات
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_AudioSystem : public UActorComponent
{
    GENERATED_BODY()

public:
    UNAR_AudioSystem();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // ============================================
    // التهيئة
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Audio")
    void Initialize();

    // ============================================
    // الموسيقى
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Music")
    void PlayMusic(USoundBase* MusicTrack, bool bLoop = true);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Music")
    void StopMusic();

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Music")
    void PauseMusic();

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Music")
    void ResumeMusic();

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Music")
    void FadeOutMusic(float FadeDuration = 2.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Music")
    void CrossFadeMusic(USoundBase* NewTrack, float FadeDuration = 3.0f);

    // ============================================
    // المؤثرات الصوتية
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|SFX")
    void PlaySFX(USoundBase* SFX, float VolumeMultiplier = 1.0f, float PitchMultiplier = 1.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|SFX")
    void PlaySFXAtLocation(USoundBase* SFX, FVector Location, float VolumeMultiplier = 1.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|SFX")
    void PlaySFXAttached(USoundBase* SFX, AActor* AttachTo, float VolumeMultiplier = 1.0f);

    // ============================================
    // الأصوات المحيطية
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Ambient")
    void PlayAmbient(USoundBase* AmbientSound, float VolumeMultiplier = 1.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Ambient")
    void StopAmbient();

    // ============================================
    // واجهة المستخدم
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|UI")
    void PlayUISound(USoundBase* UISound);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|UI")
    void PlayClickSound();

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|UI")
    void PlayHoverSound();

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|UI")
    void PlaySuccessSound();

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|UI")
    void PlayErrorSound();

    // ============================================
    // الحوارات
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Dialogue")
    void PlayDialogue(USoundBase* DialogueLine, float VolumeMultiplier = 1.0f);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Dialogue")
    void StopDialogue();

    // ============================================
    // إدارة مستوى الصوت
    // ============================================
    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Volume")
    void SetMasterVolume(float Volume);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Volume")
    void SetMusicVolume(float Volume);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Volume")
    void SetSFXVolume(float Volume);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Volume")
    void SetAmbientVolume(float Volume);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Volume")
    void SetUIVolume(float Volume);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Volume")
    void SetDialogueVolume(float Volume);

    UFUNCTION(BlueprintCallable, Category = "NAR|Audio|Volume")
    void ToggleMute();

    UFUNCTION(BlueprintPure, Category = "NAR|Audio|Volume")
    FAudioSettings GetAudioSettings() const { return Settings; }

    UFUNCTION(BlueprintPure, Category = "NAR|Audio|Volume")
    bool IsMuted() const { return Settings.bMuted; }

    // ============================================
    // أحداث
    // ============================================
    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnMusicStarted);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Audio|Events")
    FOnMusicStarted OnMusicStarted;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnMusicStopped);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Audio|Events")
    FOnMusicStopped OnMusicStopped;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnMuteToggled);
    UPROPERTY(BlueprintAssignable, Category = "NAR|Audio|Events")
    FOnMuteToggled OnMuteToggled;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "NAR|Audio|Settings")
    FAudioSettings Settings;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|Audio|Active")
    class UAudioComponent* CurrentMusicComponent = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|Audio|Active")
    class UAudioComponent* AmbientComponent = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|Audio|Active")
    class UAudioComponent* DialogueComponent = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "NAR|Audio|Active")
    USoundBase* CurrentMusicTrack = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Audio|Defaults")
    USoundBase* DefaultClickSound = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Audio|Defaults")
    USoundBase* DefaultHoverSound = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Audio|Defaults")
    USoundBase* DefaultSuccessSound = nullptr;

    UPROPERTY(EditDefaultsOnly, Category = "NAR|Audio|Defaults")
    USoundBase* DefaultErrorSound = nullptr;

private:
    void UpdateVolumes();
    float GetEffectiveVolume(EAudioType Type) const;
};
