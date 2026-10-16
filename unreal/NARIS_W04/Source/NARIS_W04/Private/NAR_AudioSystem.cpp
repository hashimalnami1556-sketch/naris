// NAR_AudioSystem.cpp — تنفيذ نظام الصوت
#include "NAR_AudioSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundBase.h"

UNAR_AudioSystem::UNAR_AudioSystem()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_AudioSystem::BeginPlay()
{
    Super::BeginPlay();
    Initialize();
}

void UNAR_AudioSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    UpdateVolumes();
}

void UNAR_AudioSystem::Initialize()
{
    UpdateVolumes();
    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] نظام الصوت جاهز"));
}

// ============================================
// الموسيقى
// ============================================
void UNAR_AudioSystem::PlayMusic(USoundBase* MusicTrack, bool bLoop)
{
    if (!MusicTrack) return;

    StopMusic();

    CurrentMusicTrack = MusicTrack;
    CurrentMusicComponent = UGameplayStatics::SpawnSound2D(
        GetWorld(),
        MusicTrack,
        GetEffectiveVolume(EAudioType::Music),
        1.0f,
        0.0f,
        nullptr,
        bLoop
    );

    OnMusicStarted.Broadcast();
    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] تشغيل موسيقى: %s"), *MusicTrack->GetName());
}

void UNAR_AudioSystem::StopMusic()
{
    if (CurrentMusicComponent)
    {
        CurrentMusicComponent->Stop();
        CurrentMusicComponent = nullptr;
    }

    OnMusicStopped.Broadcast();
    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] توقفت الموسيقى"));
}

void UNAR_AudioSystem::PauseMusic()
{
    if (CurrentMusicComponent && CurrentMusicComponent->IsPlaying())
    {
        CurrentMusicComponent->Pause();
        UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] تم إيقاف الموسيقى مؤقتاً"));
    }
}

void UNAR_AudioSystem::ResumeMusic()
{
    if (CurrentMusicComponent && !CurrentMusicComponent->IsPlaying())
    {
        CurrentMusicComponent->Play();
        UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] استئناف الموسيقى"));
    }
}

void UNAR_AudioSystem::FadeOutMusic(float FadeDuration)
{
    if (CurrentMusicComponent && CurrentMusicComponent->IsPlaying())
    {
        CurrentMusicComponent->FadeOut(FadeDuration, 0.0f);
        UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] تلاشي الموسيقى: %.2f ثانية"), FadeDuration);
    }
}

void UNAR_AudioSystem::CrossFadeMusic(USoundBase* NewTrack, float FadeDuration)
{
    if (!NewTrack) return;

    FadeOutMusic(FadeDuration);

    FTimerHandle TimerHandle;
    GetWorld()->GetTimerManager().SetTimer(
        TimerHandle,
        [this, NewTrack]()
        {
            PlayMusic(NewTrack);
        },
        FadeDuration,
        false
    );
}

// ============================================
// المؤثرات الصوتية
// ============================================
void UNAR_AudioSystem::PlaySFX(USoundBase* SFX, float VolumeMultiplier, float PitchMultiplier)
{
    if (!SFX) return;

    UGameplayStatics::PlaySound2D(
        GetWorld(),
        SFX,
        GetEffectiveVolume(EAudioType::SFX) * VolumeMultiplier,
        PitchMultiplier
    );

    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] مؤثر صوتي: %s (الصوت: %.2f, التردد: %.2f)"),
        *SFX->GetName(), VolumeMultiplier, PitchMultiplier);
}

void UNAR_AudioSystem::PlaySFXAtLocation(USoundBase* SFX, FVector Location, float VolumeMultiplier)
{
    if (!SFX) return;

    UGameplayStatics::PlaySoundAtLocation(
        GetWorld(),
        SFX,
        Location,
        1.0f,
        1.0f,
        0.0f,
        nullptr,
        nullptr,
        nullptr
    );

    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] مؤثر صوتي في الموقع: %s"), *SFX->GetName());
}

void UNAR_AudioSystem::PlaySFXAttached(USoundBase* SFX, AActor* AttachTo, float VolumeMultiplier)
{
    if (!SFX || !AttachTo) return;

    UGameplayStatics::SpawnSoundAttached(
        SFX,
        AttachTo->GetRootComponent(),
        NAME_None,
        FVector::ZeroVector,
        EAttachLocation::KeepRelativeOffset,
        true,
        GetEffectiveVolume(EAudioType::SFX) * VolumeMultiplier,
        1.0f,
        0.0f
    );

    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] مؤثر صوتي مرفق: %s"), *SFX->GetName());
}

// ============================================
// الأصوات المحيطية
// ============================================
void UNAR_AudioSystem::PlayAmbient(USoundBase* AmbientSound, float VolumeMultiplier)
{
    if (!AmbientSound) return;

    StopAmbient();

    AmbientComponent = UGameplayStatics::SpawnSound2D(
        GetWorld(),
        AmbientSound,
        GetEffectiveVolume(EAudioType::Ambient) * VolumeMultiplier,
        1.0f,
        0.0f,
        nullptr,
        true
    );

    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] صوت محيطي: %s"), *AmbientSound->GetName());
}

void UNAR_AudioSystem::StopAmbient()
{
    if (AmbientComponent)
    {
        AmbientComponent->Stop();
        AmbientComponent = nullptr;
        UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] توقف الصوت المحيطي"));
    }
}

// ============================================
// واجهة المستخدم
// ============================================
void UNAR_AudioSystem::PlayUISound(USoundBase* UISound)
{
    if (!UISound) return;

    UGameplayStatics::PlaySound2D(
        GetWorld(),
        UISound,
        GetEffectiveVolume(EAudioType::UI)
    );
}

void UNAR_AudioSystem::PlayClickSound()
{
    if (DefaultClickSound)
    {
        PlayUISound(DefaultClickSound);
    }
}

void UNAR_AudioSystem::PlayHoverSound()
{
    if (DefaultHoverSound)
    {
        PlayUISound(DefaultHoverSound);
    }
}

void UNAR_AudioSystem::PlaySuccessSound()
{
    if (DefaultSuccessSound)
    {
        PlayUISound(DefaultSuccessSound);
    }
}

void UNAR_AudioSystem::PlayErrorSound()
{
    if (DefaultErrorSound)
    {
        PlayUISound(DefaultErrorSound);
    }
}

// ============================================
// الحوارات
// ============================================
void UNAR_AudioSystem::PlayDialogue(USoundBase* DialogueLine, float VolumeMultiplier)
{
    if (!DialogueLine) return;

    DialogueComponent = UGameplayStatics::SpawnSound2D(
        GetWorld(),
        DialogueLine,
        GetEffectiveVolume(EAudioType::Dialogue) * VolumeMultiplier,
        1.0f,
        0.0f,
        nullptr,
        false
    );

    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] حوار: %s"), *DialogueLine->GetName());
}

void UNAR_AudioSystem::StopDialogue()
{
    if (DialogueComponent)
    {
        DialogueComponent->Stop();
        DialogueComponent = nullptr;
        UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] توقف الحوار"));
    }
}

// ============================================
// إدارة مستوى الصوت
// ============================================
void UNAR_AudioSystem::SetMasterVolume(float Volume)
{
    Settings.MasterVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    UpdateVolumes();
    UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] مستوى الصوت الرئيسي: %.2f"), Settings.MasterVolume);
}

void UNAR_AudioSystem::SetMusicVolume(float Volume)
{
    Settings.MusicVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    UpdateVolumes();
}

void UNAR_AudioSystem::SetSFXVolume(float Volume)
{
    Settings.SFXVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    UpdateVolumes();
}

void UNAR_AudioSystem::SetAmbientVolume(float Volume)
{
    Settings.AmbientVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    UpdateVolumes();
}

void UNAR_AudioSystem::SetUIVolume(float Volume)
{
    Settings.UIVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    UpdateVolumes();
}

void UNAR_AudioSystem::SetDialogueVolume(float Volume)
{
    Settings.DialogueVolume = FMath::Clamp(Volume, 0.0f, 1.0f);
    UpdateVolumes();
}

void UNAR_AudioSystem::ToggleMute()
{
    Settings.bMuted = !Settings.bMuted;
    UpdateVolumes();
    OnMuteToggled.Broadcast();

    if (Settings.bMuted)
    {
        UE_LOG(LogTemp, Warning, TEXT("[NAR_Audio] تم كتم الصوت"));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("[NAR_Audio] إلغاء كتم الصوت"));
    }
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_AudioSystem::UpdateVolumes()
{
    if (CurrentMusicComponent)
    {
        CurrentMusicComponent->SetVolumeMultiplier(GetEffectiveVolume(EAudioType::Music));
    }

    if (AmbientComponent)
    {
        AmbientComponent->SetVolumeMultiplier(GetEffectiveVolume(EAudioType::Ambient));
    }

    if (DialogueComponent)
    {
        DialogueComponent->SetVolumeMultiplier(GetEffectiveVolume(EAudioType::Dialogue));
    }
}

float UNAR_AudioSystem::GetEffectiveVolume(EAudioType Type) const
{
    float BaseVolume = Settings.MasterVolume;

    if (Settings.bMuted)
    {
        return 0.0f;
    }

    switch (Type)
    {
        case EAudioType::Music:
            return BaseVolume * Settings.MusicVolume;
        case EAudioType::SFX:
            return BaseVolume * Settings.SFXVolume;
        case EAudioType::Ambient:
            return BaseVolume * Settings.AmbientVolume;
        case EAudioType::UI:
            return BaseVolume * Settings.UIVolume;
        case EAudioType::Dialogue:
            return BaseVolume * Settings.DialogueVolume;
        default:
            return BaseVolume;
    }
}
