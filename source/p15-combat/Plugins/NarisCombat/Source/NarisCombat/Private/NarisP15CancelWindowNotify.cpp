#include "NarisP15CancelWindowNotify.h"
#include "NarisP15CombatComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Actor.h"

void UNarisP15CancelWindowNotify::NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation,
    float TotalDuration, const FAnimNotifyEventReference& EventReference)
{
    Super::NotifyBegin(MeshComp, Animation, TotalDuration, EventReference);
    if (MeshComp && MeshComp->GetOwner())
        if (auto* Combat = MeshComp->GetOwner()->FindComponentByClass<UNarisP15CombatComponent>())
            Combat->SetCancelWindow(true, Animation);
}

void UNarisP15CancelWindowNotify::NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation,
    const FAnimNotifyEventReference& EventReference)
{
    Super::NotifyEnd(MeshComp, Animation, EventReference);
    if (MeshComp && MeshComp->GetOwner())
        if (auto* Combat = MeshComp->GetOwner()->FindComponentByClass<UNarisP15CombatComponent>())
            Combat->SetCancelWindow(false, Animation);
}
