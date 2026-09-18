#include "NarisBossPhaseComponent.h"
UNarisBossPhaseComponent::UNarisBossPhaseComponent(){PrimaryComponentTick.bCanEverTick=false;}
void UNarisBossPhaseComponent::UpdatePhase(float H,float M){if(M<=0)return;ENarisBossPhase N=H<=0?ENarisBossPhase::Defeated:(H/M<=Phase3HealthPercent?ENarisBossPhase::Phase3:(H/M<=Phase2HealthPercent?ENarisBossPhase::Phase2:ENarisBossPhase::Phase1));if(N!=CurrentPhase){CurrentPhase=N;OnPhaseChanged.Broadcast(N);}}
void UNarisBossPhaseComponent::Defeat(){if(CurrentPhase!=ENarisBossPhase::Defeated){CurrentPhase=ENarisBossPhase::Defeated;OnPhaseChanged.Broadcast(CurrentPhase);}}
