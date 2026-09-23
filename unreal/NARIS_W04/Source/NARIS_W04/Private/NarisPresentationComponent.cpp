#include "NarisPresentationComponent.h"

#include "Camera/CameraShakeBase.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "Sound/SoundBase.h"

UNarisPresentationComponent::UNarisPresentationComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

const FNarisPresentationCue* UNarisPresentationComponent::FindCue(FName CueId) const
{
    if (CueId.IsNone())
    {
        return nullptr;
    }

    return Cues.FindByPredicate(
        [CueId](const FNarisPresentationCue& Cue)
        {
            return Cue.CueId == CueId;
        }
    );
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
        // A missing authored payload is valid for smoke/source builds.
        // The cue delegate remains the stable Blueprint/Sequencer integration point.
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
