#include "NarisInteractionComponent.h"

#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "NarisInteractable.h"

UNarisInteractionComponent::UNarisInteractionComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

AActor* UNarisInteractionComponent::FindNearestInteractable() const
{
    if (!GetOwner() || !GetWorld())
    {
        return nullptr;
    }

    const FVector Origin = GetOwner()->GetActorLocation();
    float BestDistanceSq = Radius * Radius;
    AActor* BestActor = nullptr;

    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        AActor* Candidate = *It;
        if (!Candidate || Candidate == GetOwner())
        {
            continue;
        }

        if (!Candidate->GetClass()->ImplementsInterface(UNarisInteractable::StaticClass()))
        {
            continue;
        }

        const float DistanceSq =
            FVector::DistSquared(Candidate->GetActorLocation(), Origin);

        if (DistanceSq < BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            BestActor = Candidate;
        }
    }

    return BestActor;
}

bool UNarisInteractionComponent::Interact()
{
    AActor* Target = FindNearestInteractable();
    if (!Target)
    {
        return false;
    }

    const bool bHandled = INarisInteractable::Execute_Interact(Target, GetOwner());
    if (bHandled)
    {
        OnInteracted.Broadcast(Target);
    }

    return bHandled;
}
