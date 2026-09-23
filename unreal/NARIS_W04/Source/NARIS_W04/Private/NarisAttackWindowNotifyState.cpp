#include "NarisAttackWindowNotifyState.h"

#include "Components/SkeletalMeshComponent.h"
#include "NarisHeroCharacter.h"

void UNarisAttackWindowNotifyState::NotifyBegin(
    USkeletalMeshComponent* MeshComp,
    UAnimSequenceBase* Animation,
    float TotalDuration,
    const FAnimNotifyEventReference& EventReference
)
{
    Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);

    if (!MeshComp)
    {
        return;
    }

    if (ANarisHeroCharacter* Hero =
            Cast<ANarisHeroCharacter>(MeshComp->GetOwner()))
    {
        Hero->OpenAttackHitWindow();
    }
}

void UNarisAttackWindowNotifyState::NotifyEnd(
    USkeletalMeshComponent* MeshComp,
    UAnimSequenceBase* Animation,
    const FAnimNotifyEventReference& EventReference
)
{
    if (MeshComp)
    {
        if (ANarisHeroCharacter* Hero =
                Cast<ANarisHeroCharacter>(MeshComp->GetOwner()))
        {
            Hero->CloseAttackHitWindow();
        }
    }

    Super::NotifyEnd(MeshComp, Animation, EventReference);
}
