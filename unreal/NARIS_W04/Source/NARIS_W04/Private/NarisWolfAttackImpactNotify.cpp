#include "NarisWolfAttackImpactNotify.h"

#include "CelestialWolf.h"
#include "Components/SkeletalMeshComponent.h"

void UNarisWolfAttackImpactNotify::Notify(
    USkeletalMeshComponent* MeshComp,
    UAnimSequenceBase* Animation,
    const FAnimNotifyEventReference& EventReference
)
{
    Super::Notify(MeshComp, Animation, EventReference);

    if (!MeshComp)
    {
        return;
    }

    if (ACelestialWolf* Wolf = Cast<ACelestialWolf>(MeshComp->GetOwner()))
    {
        Wolf->CommitAttackImpact();
    }
}
