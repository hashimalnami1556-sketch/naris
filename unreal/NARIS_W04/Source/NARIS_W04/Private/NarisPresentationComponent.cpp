#include "NarisPresentationComponent.h"

#include "Camera/CameraShakeBase.h"
#include "NarisGameUserSettings.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
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
        const UNarisGameUserSettings* Settings =
            UNarisGameUserSettings::GetNarisGameUserSettings();
        const float SFXScale = Settings
            ? Settings->GetPresentationSFXScale()
            : 1.f;

        UGameplayStatics::PlaySoundAtLocation(
            this,
            Cue->Sound,
            WorldLocation,
            Cue->VolumeMultiplier * SFXScale,
            Cue->PitchMultiplier,
            0.f,
            nullptr,
            nullptr
        );
    }

    if (Cue->CameraShake && GetWorld())
    {
        const UNarisGameUserSettings* Settings =
            UNarisGameUserSettings::GetNarisGameUserSettings();
        const float UserShakeScale = Settings
            ? Settings->GetEffectiveCameraShakeScale()
            : 1.f;

        APlayerController* PlayerController =
            GetWorld()->GetFirstPlayerController();
        APlayerCameraManager* CameraManager =
            PlayerController ? PlayerController->PlayerCameraManager : nullptr;

        if (CameraManager && UserShakeScale > 0.f)
        {
            const float InnerRadius = FMath::Max(0.f, Cue->ShakeInnerRadius);
            const float OuterRadius =
                FMath::Max(InnerRadius, Cue->ShakeOuterRadius);
            const float Distance = FVector::Distance(
                CameraManager->GetCameraLocation(),
                WorldLocation
            );

            float SpatialScale = 1.f;
            if (Distance > InnerRadius)
            {
                if (OuterRadius <= InnerRadius || Distance >= OuterRadius)
                {
                    SpatialScale = 0.f;
                }
                else
                {
                    const float Alpha = 1.f - (
                        (Distance - InnerRadius)
                        / FMath::Max(OuterRadius - InnerRadius, 1.f)
                    );
                    SpatialScale = FMath::Pow(
                        FMath::Clamp(Alpha, 0.f, 1.f),
                        FMath::Max(Cue->ShakeFalloff, 0.f)
                    );
                }
            }

            const float EffectiveScale = UserShakeScale * SpatialScale;
            if (EffectiveScale > KINDA_SMALL_NUMBER)
            {
                CameraManager->StartCameraShake(
                    Cue->CameraShake,
                    EffectiveScale,
                    ECameraShakePlaySpace::CameraLocal,
                    FRotator::ZeroRotator
                );
            }
        }
    }

    return true;
}
