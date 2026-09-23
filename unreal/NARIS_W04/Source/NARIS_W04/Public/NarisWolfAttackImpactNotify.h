#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "NarisWolfAttackImpactNotify.generated.h"

UCLASS(meta=(DisplayName="NARIS Celestial Wolf Attack Impact"))
class NARIS_W04_API UNarisWolfAttackImpactNotify : public UAnimNotify
{
    GENERATED_BODY()

public:
    virtual void Notify(
        USkeletalMeshComponent* MeshComp,
        UAnimSequenceBase* Animation,
        const FAnimNotifyEventReference& EventReference
    ) override;
};
