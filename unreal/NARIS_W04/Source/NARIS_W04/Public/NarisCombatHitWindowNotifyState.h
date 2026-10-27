#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "NarisCombatHitWindowNotifyState.generated.h"

/** Add to an attack montage's notify track, spanning only active hit frames. */
UCLASS(meta=(DisplayName="NARIS Combat Hit Window"))
class NARIS_W04_API UNarisCombatHitWindowNotifyState : public UAnimNotifyState
{
 GENERATED_BODY()
public:
 virtual void NotifyBegin(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation,
                          float TotalDuration, const FAnimNotifyEventReference& EventReference) override;
 virtual void NotifyEnd(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation,
                        const FAnimNotifyEventReference& EventReference) override;
};
