#include "NarisWolfAttackImpactNotify.h"

#include "CelestialWolf.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
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
#if !UE_BUILD_SHIPPING
        if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeMontageOnce")))
        {
            UE_LOG(LogTemp, Display,
                TEXT("NARIS_WOLF_COMBAT_PROBE event=MontageNotify authority=%d anim=%s"),
                Wolf->HasAuthority() ? 1 : 0,
                Animation ? *Animation->GetName() : TEXT("null"));
        }
#endif
        Wolf->CommitAttackImpact();
    }
}
