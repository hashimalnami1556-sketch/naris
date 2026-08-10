#include "BoneBeastPhaseComponent.h"

void UBoneBeastPhaseComponent::SetAuthoritativePhase(ENarisBossPhase NewPhase)
{
    if (NewPhase == MirroredPhase)
    {
        return;
    }

    MirroredPhase = NewPhase;
    OnPhaseTransition.Broadcast(FName(*UEnum::GetValueAsString(NewPhase)));
}
