#include "NarisLockOnComponent.h"

#include "BoneBeastBoss.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "NarisCombatComponent.h"

UNarisLockOnComponent::UNarisLockOnComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UNarisLockOnComponent::AcquireTarget()
{
    APawn* OwnerPawn = Cast<APawn>(GetOwner());
    if (!OwnerPawn || !GetWorld())
    {
        return false;
    }

    const FVector Origin = OwnerPawn->GetActorLocation();
    const FVector Forward = OwnerPawn->GetActorForwardVector();
    float BestScore = FLT_MAX;
    AActor* Best = nullptr;

    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        AActor* Candidate = *It;
        if (!Candidate || Candidate == GetOwner())
        {
            continue;
        }

        bool bTargetable = false;

        if (UNarisCombatComponent* Combat =
                Candidate->FindComponentByClass<UNarisCombatComponent>())
        {
            bTargetable = Combat->Health > 0.f;
        }

        if (ABoneBeastBoss* Boss = Cast<ABoneBeastBoss>(Candidate))
        {
            bTargetable =
                Boss->IsEncounterActive()
                && !Boss->IsEncounterComplete()
                && Boss->GetCurrentHealth() > 0.f;
        }

        if (!bTargetable)
        {
            continue;
        }

        const FVector ToTarget = Candidate->GetActorLocation() - Origin;
        const float Distance = ToTarget.Size();
        if (Distance > MaxDistance || Distance < 1.f)
        {
            continue;
        }

        const float Dot = FVector::DotProduct(
            Forward,
            ToTarget.GetSafeNormal()
        );
        const float Angle = FMath::RadiansToDegrees(
            FMath::Acos(FMath::Clamp(Dot, -1.f, 1.f))
        );
        if (Angle > MaxAngleDegrees)
        {
            continue;
        }

        const float Score = Distance + Angle * 8.f;
        if (Score < BestScore)
        {
            BestScore = Score;
            Best = Candidate;
        }
    }

    Target = Best;
    return IsValid(Target);
}

void UNarisLockOnComponent::ClearTarget()
{
    Target = nullptr;
}
