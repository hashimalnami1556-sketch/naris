#include "BoneBeastAttackImpactNotify.h"

#include "BoneBeastBoss.h"
#include "Components/SkeletalMeshComponent.h"
#include "Kismet/GameplayStatics.h"

void UBoneBeastAttackImpactNotify::Notify(
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

    ABoneBeastBoss* Boss = Cast<ABoneBeastBoss>(MeshComp->GetOwner());
    if (!Boss)
    {
        return;
    }

    AActor* Target = UGameplayStatics::GetPlayerPawn(Boss, 0);
    Boss->CommitAttackImpact(Target);
}
