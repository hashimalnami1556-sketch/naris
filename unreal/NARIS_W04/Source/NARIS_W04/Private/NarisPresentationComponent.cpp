#include "NarisPresentationComponent.h"

#include "Camera/CameraShakeBase.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "Sound/SoundBase.h"

namespace
{
    bool PresentationCueMatches(FName Pattern, FName Actual)
    {
        if (Pattern == Actual)
        {
            return true;
        }

        const FString PatternString = Pattern.ToString();
        if (!PatternString.EndsWith(TEXT(".*")))
        {
            return false;
        }

        const FString Prefix = PatternString.LeftChop(1);
        return Actual.ToString().StartsWith(Prefix);
    }
}

UNarisPresentationComponent::UNarisPresentationComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    DefaultProfilePath = FSoftObjectPath(
        TEXT("/Game/NARIS/W04/Presentation/DA_W04_Presentation.DA_W04_Presentation")
    );
}

void UNarisPresentationComponent::BeginPlay()
{
    Super::BeginPlay();

    if (!Profile
        && bAutoLoadDefaultProfile
        && DefaultProfilePath.IsValid())
    {
        Profile = Cast<UNarisPresentationProfile>(
            DefaultProfilePath.TryLoad()
        );
    }
}

const FNarisPresentationCue* UNarisPresentationComponent::FindCue(FName CueId) const
{
    if (CueId.IsNone())
    {
        return nullptr;
    }

    const FNarisPresentationCue* LocalCue = Cues.FindByPredicate(
        [CueId](const FNarisPresentationCue& Cue)
        {
            return PresentationCueMatches(Cue.CueId, CueId);
        }
    );

    if (LocalCue)
    {
        return LocalCue;
    }

    if (Profile)
    {
        return Profile->Cues.FindByPredicate(
            [CueId](const FNarisPresentationCue& Cue)
            {
                return PresentationCueMatches(Cue.CueId, CueId);
            }
        );
    }

    return nullptr;
}

bool UNarisPresentationComponent::HasCue(FName CueId) const
{
    return FindCue(CueId) != nullptr;
}

bool UNarisPresentationComponent::TriggerCue(FName CueId)
{
    const AActor* Owner = GetOwner();
    const FVector Location = Owner ? Owner->GetActorLocation() : FVector::ZeroVector;
    return TriggerCueAtLocation(CueId, Location);
}

bool UNarisPresentationComponent::TriggerCueAtLocation(
    FName CueId,
    FVector WorldLocation
)
{
    if (CueId.IsNone())
    {
        return false;
    }

    OnCueTriggered.Broadcast(CueId, WorldLocation);

    const FNarisPresentationCue* Cue = FindCue(CueId);
    if (!Cue)
    {
        return true;
    }

    if (Cue->NiagaraSystem)
    {
        UNiagaraFunctionLibrary::SpawnSystemAtLocation(
            this,
            Cue->NiagaraSystem,
            WorldLocation,
            FRotator::ZeroRotator,
            FVector::OneVector,
            true,
            true,
            ENCPoolMethod::AutoRelease,
            true
        );
    }

    if (Cue->Sound)
    {
        UGameplayStatics::PlaySoundAtLocation(
            this,
            Cue->Sound,
            WorldLocation,
            Cue->VolumeMultiplier,
            Cue->PitchMultiplier,
            0.f,
            nullptr,
            nullptr
        );
    }

    if (Cue->CameraShake)
    {
        UGameplayStatics::PlayWorldCameraShake(
            this,
            Cue->CameraShake,
            WorldLocation,
            FMath::Max(0.f, Cue->ShakeInnerRadius),
            FMath::Max(Cue->ShakeInnerRadius, Cue->ShakeOuterRadius),
            FMath::Max(0.f, Cue->ShakeFalloff),
            false
        );
    }

    return true;
}
