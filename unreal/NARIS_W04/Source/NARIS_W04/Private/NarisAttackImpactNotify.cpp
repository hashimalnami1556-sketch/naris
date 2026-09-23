#include "NarisAttackImpactNotify.h"

#include "Components/SkeletalMeshComponent.h"
#include "NarisHeroCharacter.h"

void UNarisAttackImpactNotify::Notify(
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

    if (ANarisHeroCharacter* Hero =
            Cast<ANarisHeroCharacter>(MeshComp->GetOwner()))
    {
        Hero->CommitPendingAttackHit();
    }
}
