#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "BoneBeastAttackImpactNotify.generated.h"

UCLASS(meta=(DisplayName="NARIS Bone Beast Attack Impact"))
class NARIS_W04_API UBoneBeastAttackImpactNotify : public UAnimNotify
{
    GENERATED_BODY()

public:
    virtual void Notify(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        const FAnimNotifyEventReference& EventReference
    ) override;
};
