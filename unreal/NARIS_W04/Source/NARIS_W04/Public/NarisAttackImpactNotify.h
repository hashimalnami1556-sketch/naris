#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "NarisAttackImpactNotify.generated.h"

UCLASS(meta=(DisplayName="NARIS Attack Impact"))
class NARIS_W04_API UNarisAttackImpactNotify : public UAnimNotify
{
    GENERATED_BODY()

public:
    virtual void Notify(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        const FAnimNotifyEventReference& EventReference
    ) override;
};
